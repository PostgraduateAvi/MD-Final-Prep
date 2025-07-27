#!/usr/bin/env python3
"""Generate embeddings from tokenized content using OpenAI API.

This script reads `tokenized_content.json` produced by `simple_tokenize.py` or
`tokenize_content.py`, calls the OpenAI embedding endpoint on each text chunk,
and stores the resulting vectors alongside metadata.

Usage:
    export OPENAI_API_KEY=your_api_key
    python3 generate_embeddings.py

The output `embeddings.jsonl` contains one JSON object per chunk with fields:
    - id: unique identifier
    - category: content category (e.g., "guidelines")
    - filename: source file
    - text: chunk text
    - embedding: list of floats
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

import openai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TOKENIZED_FILE = Path("tokenized_content.json")
OUTPUT_FILE = Path("embeddings.jsonl")
MODEL = "text-embedding-ada-002"


def load_tokenized_content() -> Dict[str, List[Dict[str, Any]]]:
    if not TOKENIZED_FILE.exists():
        logger.error(f"{TOKENIZED_FILE} not found. Run tokenization first.")
        raise FileNotFoundError(TOKENIZED_FILE)
    with open(TOKENIZED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(model=MODEL, input=text)
    return response["data"][0]["embedding"]


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    openai.api_key = api_key

    data = load_tokenized_content()
    logger.info("Loaded tokenized content")

    chunk_id = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for category, files in data.items():
            for file_info in files:
                filename = file_info["filename"]
                for chunk in file_info.get("chunks", []):
                    try:
                        embedding = generate_embedding(chunk)
                    except Exception as e:
                        logger.error(f"Embedding failed for {filename}: {e}")
                        continue
                    record = {
                        "id": chunk_id,
                        "category": category,
                        "filename": filename,
                        "text": chunk,
                        "embedding": embedding,
                    }
                    out_f.write(json.dumps(record) + "\n")
                    chunk_id += 1
    logger.info(f"Embeddings saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
