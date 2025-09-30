"""Product Buy Auditor CLI.

This module provides a command line utility for evaluating products against a
use-case. It supports JSON and CSV input files, produces Markdown, JSON and
CSV reports and includes doctested utility helpers.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


DEFAULT_WEIGHTS = {
    "fit": 0.30,
    "performance": 0.25,
    "reliability": 0.15,
    "vfm": 0.25,
    "risk": -0.10,
}


Verdict = str


def clamp(value: float, lower: float = 0.0, upper: float = 10.0) -> float:
    """Clamp *value* to the inclusive range ``[lower, upper]``.

    >>> clamp(11.2)
    10.0
    >>> clamp(-1.0)
    0.0
    >>> clamp(5.5, 5.0, 6.0)
    5.5
    """

    return max(lower, min(upper, value))


def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide ``numerator`` by ``denominator``.

    Returns 0 when ``denominator`` is 0 to avoid ``ZeroDivisionError``.
    """

    if denominator == 0:
        return 0.0
    return numerator / denominator


def parse_rule(rule: str) -> Tuple[str, str, Optional[float]]:
    """Parse a must-have or nice-to-have rule string.

    >>> parse_rule("warranty>=12m")
    ('warranty', '>=', 12.0)
    >>> parse_rule("weight<=2.5kg")
    ('weight', '<=', 2.5)
    >>> parse_rule("attachments:crevice")
    ('attachments', ':', 'crevice')
    """

    if ":" in rule:
        key, value = rule.split(":", 1)
        return key.strip(), ":", None if not value else value.strip()
    for op in (">=", "<=", ">", "<"):
        if op in rule:
            key, value = rule.split(op, 1)
            cleaned = "".join(ch for ch in value if (ch.isdigit() or ch == "."))
            return key.strip(), op, float(cleaned) if cleaned else None
    return rule.strip(), "==", None


def verdict_from_score(score: float, hard_fail: bool = False) -> Verdict:
    """Map a numerical score to a textual verdict.

    >>> verdict_from_score(8.2)
    'BUY'
    >>> verdict_from_score(7.4)
    'CONSIDER'
    >>> verdict_from_score(6.5)
    'ONLY IF DISCOUNTED / NICHE'
    >>> verdict_from_score(5.9)
    'SKIP'
    >>> verdict_from_score(9.0, hard_fail=True)
    'SKIP'
    """

    if hard_fail:
        return "SKIP"
    if score >= 8.0:
        return "BUY"
    if score >= 7.0:
        return "CONSIDER"
    if score >= 6.0:
        return "ONLY IF DISCOUNTED / NICHE"
    return "SKIP"


def log_rating_factor(count: int) -> float:
    """Return a log-scaled factor for the provided review ``count``.

    ``count`` is clamped to a minimum of 1 to avoid math domain errors.

    >>> round(log_rating_factor(10), 2)
    1.0
    >>> round(log_rating_factor(100), 2)
    2.0
    >>> round(log_rating_factor(10_000), 2)
    4.0
    """

    return math.log10(max(1, count))


def z_normalize(values: Iterable[float]) -> List[float]:
    """Return a z-score normalized list for the iterable of ``values``.

    >>> z_normalize([1, 1, 1])
    [0.0, 0.0, 0.0]
    >>> [round(v, 2) for v in z_normalize([1, 2, 3])]
    [-1.22, 0.0, 1.22]
    """

    values_list = list(values)
    if not values_list:
        return []
    mean = statistics.mean(values_list)
    stdev = statistics.pstdev(values_list)
    if stdev == 0:
        return [0.0 for _ in values_list]
    return [(value - mean) / stdev for value in values_list]


def infer_confidence(total_fields: int, missing_fields: int) -> float:
    """Estimate a confidence score based on missing data.

    >>> infer_confidence(10, 0)
    1.0
    >>> infer_confidence(10, 5)
    0.5
    >>> infer_confidence(0, 0)
    0.0
    """

    if total_fields == 0:
        return 0.0
    return clamp(1.0 - (missing_fields / total_fields), 0.0, 1.0)


def evaluate_rule(rule: str, product: Dict[str, Any]) -> Tuple[bool, str]:
    """Evaluate a rule string against a product.

    Returns a tuple of ``(result, detail)``.
    """

    key, op, value = parse_rule(rule)
    specs = product.get("specs", {})
    if key in product:
        source = product
    else:
        source = specs
    raw = source.get(key)
    if op == ":":
        if isinstance(raw, list):
            passed = value in raw
        elif isinstance(raw, str):
            passed = (value or "").lower() in raw.lower()
        else:
            passed = False
        return passed, f"needs {value}"
    if raw is None:
        return False, "missing"
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        try:
            numeric = float("".join(ch for ch in str(raw) if ch.isdigit() or ch == "."))
        except ValueError:
            return False, "not comparable"
    if value is None:
        return False, "no target"
    if op == ">=":
        return numeric >= value, f">={value}"
    if op == "<=":
        return numeric <= value, f"<={value}"
    if op == ">":
        return numeric > value, f">{value}"
    if op == "<":
        return numeric < value, f"<{value}"
    return str(raw).lower() == str(value).lower(), f"=={value}"


RubricFunc = Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], Tuple[str, float, str]]


def _score_speaker(product: Dict[str, Any], usecase: Dict[str, Any], weights: Dict[str, float]) -> List[Tuple[str, float, str]]:
    specs = product.get("specs", {})
    price = product.get("price_inr") or product.get("price")
    entries = []

    watts = specs.get("sound_watts_rms") or specs.get("output_watts")
    if watts is not None:
        try:
            watts_val = float(watts)
            score = clamp((watts_val / 10.0) * 5)
        except (TypeError, ValueError):
            score = 5.0
    else:
        score = 5.0
    entries.append(("Sound", score, "output watts proxy"))

    battery = specs.get("battery_life_hr") or specs.get("battery")
    if battery is not None:
        try:
            battery_val = float(battery)
            score = clamp((battery_val / 8.0) * 6)
        except (TypeError, ValueError):
            score = 5.0
    else:
        score = 4.5
    entries.append(("Battery", score, "runtime estimate"))

    warranty = specs.get("warranty_months") or product.get("warranty_months")
    if warranty is not None:
        try:
            warranty_val = float(warranty)
            score = clamp((warranty_val / 12.0) * 5)
        except (TypeError, ValueError):
            score = 5.0
    else:
        score = 4.0
    entries.append(("Build", score, "warranty proxy"))

    wireless = specs.get("wireless") or specs.get("connectivity")
    if isinstance(wireless, str):
        score = 7.5 if "5" in wireless else 6.0
    else:
        score = 5.0
    entries.append(("Connectivity", score, "wireless spec"))

    if price:
        try:
            price_val = float(price)
            price_score = clamp(10 - (price_val / 5000) * 3)
        except (TypeError, ValueError):
            price_score = 6.0
    else:
        price_score = 5.0
    entries.append(("Value", clamp(price_score, 0, 10), "price tier"))
    return entries


def _score_vacuum(product: Dict[str, Any], usecase: Dict[str, Any], weights: Dict[str, float]) -> List[Tuple[str, float, str]]:
    specs = product.get("specs", {})
    entries = []
    motor = specs.get("motor_watts") or specs.get("suction_airwatts")
    if motor is not None:
        try:
            motor_val = float(motor)
            entries.append(("Suction", clamp((motor_val / 150.0) * 8), "motor watts"))
        except (TypeError, ValueError):
            entries.append(("Suction", 5.0, "unknown"))
    else:
        entries.append(("Suction", 4.5, "missing"))

    runtime = specs.get("runtime_minutes") or specs.get("battery_life_hr")
    if runtime is not None:
        try:
            runtime_val = float(runtime) * (60 if runtime == specs.get("battery_life_hr") else 1)
            entries.append(("Battery", clamp((runtime_val / 35.0) * 7), "runtime"))
        except (TypeError, ValueError):
            entries.append(("Battery", 5.0, "unknown"))
    else:
        entries.append(("Battery", 4.5, "missing"))

    weight = specs.get("weight_kg") or specs.get("weight")
    if weight is not None:
        try:
            weight_val = float(weight)
            entries.append(("Ergonomics", clamp(10 - (weight_val * 3.5)), "weight"))
        except (TypeError, ValueError):
            entries.append(("Ergonomics", 5.0, "unknown"))
    else:
        entries.append(("Ergonomics", 5.0, "missing"))

    attachments = specs.get("attachments") or []
    if isinstance(attachments, list):
        has_crevice = "crevice" in [a.lower() for a in attachments]
        has_upholstery = "upholstery" in [a.lower() for a in attachments]
        count = sum([has_crevice, has_upholstery])
        entries.append(("Attachments", clamp(5 + count * 2.5), "attachments"))
    else:
        entries.append(("Attachments", 4.0, "missing"))

    warranty = specs.get("warranty_months") or product.get("warranty_months")
    if warranty is not None:
        try:
            warranty_val = float(warranty)
            entries.append(("Reliability", clamp((warranty_val / 12.0) * 5), "warranty"))
        except (TypeError, ValueError):
            entries.append(("Reliability", 5.0, "unknown"))
    else:
        entries.append(("Reliability", 4.5, "missing"))
    return entries


RUBRIC_REGISTRY: Dict[str, Callable[[Dict[str, Any], Dict[str, Any], Dict[str, float]], List[Tuple[str, float, str]]]] = {
    "speaker": _score_speaker,
    "vacuum": _score_vacuum,
}


@dataclass
class ScoreBreakdown:
    name: str
    details: List[Tuple[str, float, str]]

    def mean_score(self) -> float:
        if not self.details:
            return 0.0
        return sum(score for _, score, _ in self.details) / len(self.details)


@dataclass
class ProductEvaluation:
    product: Dict[str, Any]
    fit: float
    performance_breakdown: ScoreBreakdown
    reliability: float
    vfm: float
    risk: float
    final_score: float
    confidence: float
    hard_fail: bool
    verdict: Verdict
    missing: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_products(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = load_json(path)
        if not isinstance(data, list):
            raise ValueError("Product JSON must be a list of objects")
        return data
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            return [row for row in reader]
    raise ValueError("Unsupported product file format. Use JSON or CSV.")


def load_weights(path: Optional[Path]) -> Dict[str, float]:
    if path is None:
        return dict(DEFAULT_WEIGHTS)
    weights = load_json(path)
    merged = dict(DEFAULT_WEIGHTS)
    merged.update({k.lower(): v for k, v in weights.items()})
    return merged


def compute_fit_score(product: Dict[str, Any], usecase: Dict[str, Any]) -> Tuple[float, bool, List[str], List[str]]:
    specs = product.get("specs", {})
    missing = []
    flags = []
    notes = []
    score = 7.0
    hard_fail = False
    for rule in usecase.get("must_haves", []) or []:
        result, detail = evaluate_rule(rule, product)
        if not result:
            hard_fail = True
            flags.append(f"fails must-have: {rule}")
            score -= 2.5
    for rule in usecase.get("nice_to_haves", []) or []:
        result, _ = evaluate_rule(rule, product)
        if result:
            score += 0.6
    budget = usecase.get("budget_max_inr") or usecase.get("budget")
    price = product.get("price_inr") or product.get("price")
    if budget and price:
        try:
            price_val = float(price)
            budget_val = float(budget)
            if price_val > budget_val:
                over = (price_val - budget_val) / budget_val
                penalty = 2.0 if over > 0.1 else 0.8
                score -= penalty
                notes.append(f"over budget by {over*100:.0f}%")
        except (TypeError, ValueError):
            missing.append("price_inr")
    else:
        missing.append("price_inr")

    mandatory_fields = ["price_inr", "category", "brand", "name"]
    for field in mandatory_fields:
        if product.get(field) is None:
            missing.append(field)

    return clamp(score), hard_fail, flags, notes


def compute_reliability(product: Dict[str, Any]) -> Tuple[float, List[str]]:
    ratings = product.get("ratings") or {}
    avg = ratings.get("avg") or ratings.get("average")
    count = ratings.get("count") or ratings.get("reviews")
    warranty = product.get("warranty_months") or product.get("specs", {}).get("warranty_months")
    return_policy = product.get("return_policy_days")
    flags: List[str] = []

    score = 5.0
    if avg is not None:
        try:
            avg_val = float(avg)
            score += (avg_val - 3.6) * 1.8
            if avg_val < 3.6:
                flags.append("ratings below 3.6")
        except (TypeError, ValueError):
            flags.append("ratings avg unclear")
    else:
        flags.append("ratings missing")

    if count is not None:
        try:
            count_val = int(count)
            score += log_rating_factor(count_val)
            if count_val < 100:
                flags.append("low rating count")
        except (TypeError, ValueError):
            flags.append("ratings count unclear")
    else:
        flags.append("ratings count missing")

    if warranty is not None:
        try:
            score += clamp(float(warranty) / 12 * 2)
        except (TypeError, ValueError):
            flags.append("warranty unclear")
    if return_policy is not None:
        try:
            score += clamp(float(return_policy) / 30 * 1.5)
        except (TypeError, ValueError):
            flags.append("return policy unclear")

    return clamp(score), flags


def compute_vfm(perf_core: float, price: Optional[float], peer_prices: List[float]) -> float:
    """Compute a value-for-money score.

    >>> compute_vfm(7.5, 1500, [1000, 1200, 2000]) > 0
    True
    >>> round(compute_vfm(5.0, None, [1000, 2000]), 2)
    5.0
    """

    if price is None or not peer_prices:
        return perf_core
    median_price = statistics.median(peer_prices)
    price_norm = safe_divide(price, median_price)
    vfm_raw = safe_divide(perf_core, price_norm ** 0.6 if price_norm > 0 else 1)
    # z-normalize across peer prices to reduce extremes.
    pseudo_values = peer_prices + [price]
    z_scores = z_normalize(pseudo_values)
    if not z_scores:
        return clamp(vfm_raw)
    price_index = len(z_scores) - 1
    adjusted = vfm_raw - z_scores[price_index]
    return clamp(adjusted)


def compute_risk(product: Dict[str, Any], usecase: Dict[str, Any]) -> Tuple[float, List[str]]:
    specs = product.get("specs", {})
    price = product.get("price_inr")
    last_price = product.get("last_price_inr_30d")
    flags: List[str] = []
    risk = 0.0
    missing_critical = []
    for key in ("battery_life_hr", "warranty_months"):
        if specs.get(key) is None:
            missing_critical.append(key)
    if missing_critical:
        risk -= 0.5 * len(missing_critical)
        flags.append(f"spec gaps: {', '.join(missing_critical)}")
    if price and last_price:
        try:
            price_val = float(price)
            last_val = float(last_price)
            if price_val < last_val * 0.6 and product.get("ratings", {}).get("count", 0) < 100:
                risk -= 1.5
                flags.append("too cheap vs 30d price")
        except (TypeError, ValueError):
            flags.append("price history unclear")
    seller = product.get("seller")
    if seller and isinstance(seller, str) and "official" not in seller.lower() and "retail" not in seller.lower():
        risk -= 0.5
        flags.append(f"seller risk: {seller}")
    return clamp(risk, -5.0, 5.0), flags


def gather_missing(product: Dict[str, Any]) -> List[str]:
    missing = []
    for key in ("name", "brand", "category", "price_inr"):
        if product.get(key) is None:
            missing.append(key)
    return missing


def evaluate_product(
    product: Dict[str, Any],
    usecase: Dict[str, Any],
    weights: Dict[str, float],
    peer_prices: List[float],
) -> ProductEvaluation:
    category = (product.get("category") or usecase.get("category") or "").lower()
    rubric = RUBRIC_REGISTRY.get(category, _score_speaker)
    breakdown_entries = rubric(product, usecase, weights)
    performance_breakdown = ScoreBreakdown(name="Performance", details=breakdown_entries)
    perf_mean = performance_breakdown.mean_score()

    fit, hard_fail, fit_flags, fit_notes = compute_fit_score(product, usecase)
    reliability, reliability_flags = compute_reliability(product)

    price = product.get("price_inr") or product.get("price")
    try:
        price_val: Optional[float] = float(price) if price is not None else None
    except (TypeError, ValueError):
        price_val = None
    vfm = compute_vfm(perf_mean, price_val, peer_prices)

    risk, risk_flags = compute_risk(product, usecase)

    weight_sum = sum(abs(v) for v in weights.values()) or 1
    normalized_weights = {k: v / weight_sum for k, v in weights.items()}
    weighted = (
        fit * normalized_weights.get("fit", 0)
        + perf_mean * normalized_weights.get("performance", 0)
        + reliability * normalized_weights.get("reliability", 0)
        + vfm * normalized_weights.get("vfm", 0)
        + risk * normalized_weights.get("risk", 0)
    )
    final_score = clamp(weighted)

    missing = gather_missing(product)
    confidence = infer_confidence(12, len(missing) + len(risk_flags))
    verdict = verdict_from_score(final_score, hard_fail)
    flags = fit_flags + reliability_flags + risk_flags
    notes = fit_notes

    return ProductEvaluation(
        product=product,
        fit=fit,
        performance_breakdown=performance_breakdown,
        reliability=reliability,
        vfm=vfm,
        risk=risk,
        final_score=final_score,
        confidence=confidence,
        hard_fail=hard_fail,
        verdict=verdict,
        missing=missing,
        flags=flags,
        notes=notes,
    )


def format_micro_summary(eval_: ProductEvaluation) -> str:
    detail_pairs = [f"{name} {score:.1f}/10" for name, score, _ in eval_.performance_breakdown.details[:3]]
    detail_text = ", ".join(detail_pairs)
    decision = {
        "BUY": "Strong buy call",
        "CONSIDER": "Worth a look",
        "ONLY IF DISCOUNTED / NICHE": "Only if discounted or niche need",
        "SKIP": "Don’t buy unless emergency",
    }.get(eval_.verdict, "Don’t buy unless emergency")
    return f"{detail_text}, Final {eval_.final_score:.1f}/10 — {decision}."


def generate_markdown(evaluations: List[ProductEvaluation], top_n: Optional[int] = None) -> str:
    lines = []
    lines.append(f"Generated on {datetime.utcnow().isoformat()}Z\n")
    header = "| Rank | Product | Final | Fit | Performance | Reliability | VFM | Price | Verdict |"
    separator = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    lines.append(header)
    lines.append(separator)
    for idx, eval_ in enumerate(evaluations, 1):
        product = eval_.product
        price = product.get("price_inr") or product.get("price") or "—"
        lines.append(
            f"| {idx} | {product.get('name', 'Unknown')} | {eval_.final_score:.1f} | {eval_.fit:.1f} | "
            f"{eval_.performance_breakdown.mean_score():.1f} | {eval_.reliability:.1f} | {eval_.vfm:.1f} | {price} | {eval_.verdict} |"
        )

    shortlist = evaluations if top_n is None else evaluations[:top_n]
    for idx, eval_ in enumerate(shortlist, 1):
        product = eval_.product
        lines.append(
            f"\n### {idx}) {product.get('name', 'Unknown')} — Final {eval_.final_score:.1f}/10  (Confidence {eval_.confidence:.2f})"
        )
        perf_parts = " · ".join(
            f"{name}: {score:.1f}/10" for name, score, _ in eval_.performance_breakdown.details
        )
        lines.append(perf_parts)
        audit_line = format_micro_summary(eval_)
        lines.append(f"Audit: {audit_line}")
        flags = eval_.flags if eval_.flags else ["—"]
        lines.append(f"Flags: {', '.join(flags)}")
        mh_status = "FAIL" if eval_.hard_fail else "PASS"
        lines.append(f"Must-have check: {mh_status}")
        if eval_.notes:
            lines.append(f"Notes: {', '.join(eval_.notes)}")
    return "\n".join(lines) + "\n"


def generate_json(evaluations: List[ProductEvaluation]) -> Dict[str, Any]:
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "results": [
            {
                "product": eval_.product,
                "fit": eval_.fit,
                "performance": {
                    name: {
                        "score": score,
                        "note": note,
                    }
                    for name, score, note in eval_.performance_breakdown.details
                },
                "performance_average": eval_.performance_breakdown.mean_score(),
                "reliability": eval_.reliability,
                "vfm": eval_.vfm,
                "risk": eval_.risk,
                "final_score": eval_.final_score,
                "confidence": eval_.confidence,
                "verdict": eval_.verdict,
                "hard_fail": eval_.hard_fail,
                "flags": eval_.flags,
                "notes": eval_.notes,
            }
            for eval_ in evaluations
        ],
    }


def write_reports(
    evaluations: List[ProductEvaluation],
    output_dir: Path,
    top_n: Optional[int],
    include_csv: bool = True,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown = generate_markdown(evaluations, top_n=top_n)
    (output_dir / "audit_report.md").write_text(markdown, encoding="utf-8")
    (output_dir / "audit_report.json").write_text(
        json.dumps(generate_json(evaluations), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if include_csv:
        with (output_dir / "scores.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow([
                "name",
                "brand",
                "category",
                "final_score",
                "fit",
                "performance",
                "reliability",
                "vfm",
                "risk",
                "confidence",
                "verdict",
            ])
            for eval_ in evaluations:
                product = eval_.product
                writer.writerow(
                    [
                        product.get("name"),
                        product.get("brand"),
                        product.get("category"),
                        f"{eval_.final_score:.2f}",
                        f"{eval_.fit:.2f}",
                        f"{eval_.performance_breakdown.mean_score():.2f}",
                        f"{eval_.reliability:.2f}",
                        f"{eval_.vfm:.2f}",
                        f"{eval_.risk:.2f}",
                        f"{eval_.confidence:.2f}",
                        eval_.verdict,
                    ]
                )


def determine_category(products: List[Dict[str, Any]], explicit: Optional[str]) -> str:
    if explicit:
        return explicit.lower()
    categories = [str(prod.get("category")).lower() for prod in products if prod.get("category")]
    if not categories:
        return "speaker"
    return max(set(categories), key=categories.count)


def evaluate_products(
    products: List[Dict[str, Any]],
    usecase: Dict[str, Any],
    weights: Dict[str, float],
    category: Optional[str] = None,
) -> List[ProductEvaluation]:
    target_category = determine_category(products, category)
    peer_prices = []
    for product in products:
        if str(product.get("category", "")).lower() == target_category:
            price = product.get("price_inr") or product.get("price")
            try:
                peer_prices.append(float(price))
            except (TypeError, ValueError):
                continue
    evaluations = [
        evaluate_product(product, usecase, weights, peer_prices)
        for product in products
        if str(product.get("category", target_category)).lower() == target_category
    ]
    evaluations.sort(key=lambda e: (e.final_score, e.confidence), reverse=True)
    return evaluations


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Product Buy Auditor")
    parser.add_argument("--input", required=False, help="Path to products file (JSON or CSV)")
    parser.add_argument("--usecase", required=False, help="Path to usecase JSON file")
    parser.add_argument("--weights", required=False, help="Path to weights JSON file")
    parser.add_argument("--category", required=False, help="Override category for scoring")
    parser.add_argument("--top", type=int, default=None, help="Limit shortlist output")
    parser.add_argument("--output", default=".", help="Directory to write reports")
    parser.add_argument("--no-csv", action="store_true", help="Disable scores.csv output")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if not args.input or not args.usecase:
        print("No input/usecase specified. Running demo dataset...", file=sys.stderr)
        return run_demo()

    products_path = Path(args.input)
    usecase_path = Path(args.usecase)
    weights_path = Path(args.weights) if args.weights else None

    try:
        products = load_products(products_path)
        usecase = load_json(usecase_path)
        weights = load_weights(weights_path)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error loading inputs: {exc}", file=sys.stderr)
        return 1

    evaluations = evaluate_products(products, usecase, weights, args.category)
    if not evaluations:
        print("No products evaluated. Check category filters.", file=sys.stderr)
        return 1
    write_reports(
        evaluations,
        Path(args.output),
        top_n=args.top,
        include_csv=not args.no_csv,
    )
    print(f"Wrote reports for {len(evaluations)} products to {args.output}")
    return 0


def run_demo() -> int:
    demo_dir = Path("demo_output")
    demo_dir.mkdir(exist_ok=True)
    products = [
        {
            "name": "Boat Stone Pro",
            "brand": "boAt",
            "category": "speaker",
            "price_inr": 1799,
            "specs": {
                "sound_watts_rms": 10,
                "battery_mah": 2000,
                "battery_life_hr": 7,
                "weight_kg": 0.48,
                "wireless": "BT 5.0",
                "warranty_months": 12,
            },
            "ratings": {"avg": 4.1, "count": 12650},
            "notable_cons": ["mids recessed", "average mic"],
            "seller": "Amazon Retail",
            "return_policy_days": 7,
            "last_price_inr_30d": 1999,
        },
        {
            "name": "Budget Beats Mini",
            "brand": "BeatLabs",
            "category": "speaker",
            "price_inr": 899,
            "specs": {
                "sound_watts_rms": 6,
                "battery_life_hr": 5,
                "wireless": "BT 4.2",
            },
            "ratings": {"avg": 3.9, "count": 420},
            "seller": "OnlineBazaar",
            "return_policy_days": 10,
            "last_price_inr_30d": 1299,
        },
        {
            "name": "ProSound Max",
            "brand": "SoundMax",
            "category": "speaker",
            "price_inr": 3499,
            "specs": {
                "sound_watts_rms": 20,
                "battery_life_hr": 12,
                "wireless": "BT 5.3",
                "warranty_months": 18,
            },
            "ratings": {"avg": 4.5, "count": 8500},
            "seller": "SoundMax Official",
            "return_policy_days": 15,
            "last_price_inr_30d": 3799,
        },
        {
            "name": "NoData Speaker",
            "brand": "Mystery",
            "category": "speaker",
            "price_inr": 1500,
            "specs": {},
            "ratings": {},
            "seller": "Unknown Store",
        },
        {
            "name": "OverBudget Sonic",
            "brand": "LuxeAudio",
            "category": "speaker",
            "price_inr": 22000,
            "specs": {
                "sound_watts_rms": 40,
                "battery_life_hr": 24,
                "wireless": "BT 5.2",
                "warranty_months": 24,
            },
            "ratings": {"avg": 4.8, "count": 400},
            "seller": "Luxe Flagship",
            "last_price_inr_30d": 24000,
        },
    ]
    usecase = {
        "purpose": "Portable music indoors and travel",
        "budget_max_inr": 5000,
        "must_haves": ["wireless", "warranty>=12m"],
        "nice_to_haves": ["battery_life_hr>=10"],
        "region": "IN",
    }
    weights = dict(DEFAULT_WEIGHTS)
    evaluations = evaluate_products(products, usecase, weights)
    write_reports(evaluations, demo_dir, top_n=3)
    print(f"Demo reports written to {demo_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

