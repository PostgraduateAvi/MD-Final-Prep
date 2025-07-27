#!/usr/bin/env python3
"""FastAPI server exposing endpoints to work with MD Final Prep data."""
import subprocess
import json
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException

app = FastAPI(title="MD Final Prep API")

BASE_PATH = Path("PDFs")
TOKENIZED_PATH = Path("tokenized_content.json")
EMBEDDINGS_PATH = Path("embeddings.jsonl")


def load_tokenized_data() -> Dict:
    if not TOKENIZED_PATH.exists():
        return {}
    with open(TOKENIZED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
