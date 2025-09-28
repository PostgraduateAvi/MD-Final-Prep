#!/usr/bin/env python3
"""FastAPI server exposing endpoints for the MD Final Prep evidence explorer."""
from __future__ import annotations

import http.client
import json
import os
import subprocess
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="MD Final Prep API", version="2.0.0")

BASE_PATH = Path("PDFs")
TOKENIZED_PATH = Path("tokenized_content.json")
EMBEDDINGS_PATH = Path("embeddings.jsonl")
DATA_PATH = Path("data/evidence_sources.json")
FRONTEND_PATH = Path(__file__).parent / "frontend"


class EvidenceIdentifier(BaseModel):
    """Descriptor describing the identifier badge shown on evidence cards."""

    type: str
    label: str
    value: str
    display_text: str
    url: Optional[str]
    usable: bool


class EvidenceResult(BaseModel):
    """Structured response for the evidence search endpoint."""

    id: str
    title: str
    summary: str
    doi: Optional[str]
    original_doi: Optional[str]
    pmid: Optional[str]
    journal: Optional[str]
    year: Optional[int]
    authors: List[str]
    topics: List[str]
    source_url: Optional[str]
    doi_verified: Optional[bool]
    doi_error: bool
    identifier: EvidenceIdentifier
    viva_prompt: str


class TopicSummary(BaseModel):
    """Summary of how many evidence cards exist for a given topic tag."""

    name: str
    count: int


def load_tokenized_data() -> Dict:
    if not TOKENIZED_PATH.exists():
        return {}
    with open(TOKENIZED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache()
def load_evidence_data() -> List[Dict]:
    """Load curated evidence summaries displayed in the explorer."""

    if not DATA_PATH.exists():
        raise RuntimeError("Evidence dataset not found; ensure data/evidence_sources.json exists")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_identifier(record: Dict, doi_value: str) -> EvidenceIdentifier:
    """Create a descriptor for whichever identifier is currently usable."""

    doi_value = (doi_value or "").strip()
    if doi_value:
        return EvidenceIdentifier(
            type="doi",
            label="DOI",
            value=doi_value,
            display_text=f"DOI: {doi_value}",
            url=f"https://doi.org/{quote(doi_value)}",
            usable=True,
        )

    pmid = (record.get("pmid") or "").strip()
    if pmid:
        return EvidenceIdentifier(
            type="pmid",
            label="PMID",
            value=pmid,
            display_text=f"PMID: {pmid}",
            url=f"https://pubmed.ncbi.nlm.nih.gov/{quote(pmid)}/",
            usable=True,
        )

    return EvidenceIdentifier(
        type="none",
        label="Identifier",
        value="",
        display_text="Identifier unavailable",
        url=None,
        usable=False,
    )


def build_viva_prompt(identifier: EvidenceIdentifier, record: Dict) -> str:
    """Generate viva-style prompts that reference the selected identifier."""

    title = record.get("title", "this study")
    if identifier.type == "doi":
        return f"Viva prompt: Discuss the methodology referenced in DOI {identifier.value} from {title}."
    if identifier.type == "pmid":
        return f"Viva prompt: Summarise the clinical implications noted in PMID {identifier.value} for {title}."
    return f"Viva prompt: Outline the key findings from {title} without DOI or PMID identifiers."


def should_attempt_network_verification() -> bool:
    """Allow opt-in DOI network checks via environment variable."""

    return os.getenv("ENABLE_DOI_NETWORK_CHECKS", "0") == "1"


def head_request_to_doi(doi: str) -> bool:
    """Perform a HEAD request to determine whether a DOI resolves successfully."""

    connection: Optional[http.client.HTTPSConnection] = None
    try:
        connection = http.client.HTTPSConnection("doi.org", timeout=5.0)
        connection.request("HEAD", f"/{quote(doi)}")
        response = connection.getresponse()
        return 200 <= response.status < 400
    except Exception:
        return False
    finally:
        if connection is not None:
            connection.close()


def evaluate_doi(record: Dict, verify: bool) -> tuple[str, Optional[bool], bool]:
    """Return the active DOI value, verification flag, and whether an error occurred."""

    original = (record.get("doi") or "").strip()
    if not original:
        return "", None, False

    if not verify:
        return original, None, False

    if record.get("doi_known_bad"):
        return "", False, True

    if should_attempt_network_verification():
        is_valid = head_request_to_doi(original)
        return (original if is_valid else "", bool(is_valid), not is_valid)

    # Assume valid when network checks are disabled but keep verification metadata
    return original, True, False


def matches_query(values: Iterable[str], query: str) -> bool:
    normalized = query.strip().lower()
    if not normalized:
        return True
    for value in values:
        if normalized in value.lower():
            return True
    return False


def format_result(record: Dict, verify: bool) -> EvidenceResult:
    doi_value, doi_verified, doi_error = evaluate_doi(record, verify)
    identifier = build_identifier(record, doi_value)
    viva_prompt = build_viva_prompt(identifier, record)

    return EvidenceResult(
        id=record.get("id", ""),
        title=record.get("title", ""),
        summary=record.get("summary", ""),
        doi=doi_value or None,
        original_doi=record.get("doi") or None,
        pmid=(record.get("pmid") or None) or None,
        journal=record.get("journal"),
        year=record.get("year"),
        authors=list(record.get("authors", [])),
        topics=list(record.get("topics", [])),
        source_url=record.get("source_url"),
        doi_verified=doi_verified,
        doi_error=doi_error,
        identifier=identifier,
        viva_prompt=viva_prompt,
    )


@app.on_event("startup")
def ensure_frontend_exists() -> None:
    if not FRONTEND_PATH.exists():
        raise RuntimeError("Frontend assets missing; run repository setup before serving the API")


app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_explorer() -> HTMLResponse:
    """Serve the evidence explorer single-page app."""

    index_path = FRONTEND_PATH / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="Evidence explorer UI not found")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/files")
def list_files() -> Dict[str, list]:
    """List available PDF/Excel files grouped by folder."""
    categories = {}
    if not BASE_PATH.exists():
        return categories
    for folder in BASE_PATH.iterdir():
        if folder.is_dir():
            categories[folder.name] = sorted([p.name for p in folder.glob("*") if p.is_file()])
    return categories


@app.post("/tokenize")
def run_tokenization() -> Dict[str, str]:
    """Run simple_tokenize.py script."""
    try:
        subprocess.run(["python3", "simple_tokenize.py"], check=True)
    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"detail": "Tokenization completed"}


@app.post("/generate-embeddings")
def run_embeddings() -> Dict[str, str]:
    """Generate embeddings from tokenized content."""
    if not TOKENIZED_PATH.exists():
        raise HTTPException(status_code=400, detail="tokenized_content.json not found")
    try:
        subprocess.run(["python3", "generate_embeddings.py"], check=True)
    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"detail": "Embeddings generated"}


@app.get("/token-data")
def get_token_data(category: str, filename: str) -> Dict:
    """Return tokenization info for a specific file."""
    data = load_tokenized_data()
    if category not in data:
        raise HTTPException(status_code=404, detail="Category not found")
    for file_info in data[category]:
        if file_info.get("filename") == filename:
            return file_info
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/topics", response_model=List[TopicSummary])
def list_topics() -> List[TopicSummary]:
    """Return available evidence topics and how many cards match each."""

    counter: Counter[str] = Counter()
    for record in load_evidence_data():
        for topic in record.get("topics", []):
            counter[topic] += 1
    return [TopicSummary(name=name, count=count) for name, count in sorted(counter.items())]


@app.get("/api/search", response_model=List[EvidenceResult])
def search_evidence(
    q: str = Query("", description="Search term applied to titles, summaries, DOIs, PMIDs, and topics."),
    verify: bool = Query(True, description="When true, verify that DOIs resolve before exposing them."),
    topic: Optional[str] = Query(None, description="Restrict results to a specific topic tag."),
) -> List[EvidenceResult]:
    """Filter curated evidence records and enrich them for the explorer UI."""

    records = load_evidence_data()
    filtered: List[Dict] = []

    for record in records:
        if topic and topic not in record.get("topics", []):
            continue
        searchable_fields = [
            record.get("title", ""),
            record.get("summary", ""),
            record.get("journal", ""),
            record.get("doi", ""),
            record.get("pmid", ""),
            " ".join(record.get("topics", [])),
        ]
        if matches_query(searchable_fields, q):
            filtered.append(record)

    return [format_result(record, verify) for record in filtered]


@app.get("/api/evidence/{evidence_id}", response_model=EvidenceResult)
def get_evidence(evidence_id: str, verify: bool = Query(True)) -> EvidenceResult:
    """Return a single evidence record by identifier."""

    for record in load_evidence_data():
        if record.get("id") == evidence_id:
            return format_result(record, verify)
    raise HTTPException(status_code=404, detail="Evidence record not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
