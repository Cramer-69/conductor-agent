"""Read-only source-file ingestion for the local filing cabinet."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

from cabinet.store import CabinetStore


TEXT_EXTENSIONS = {
    ".csv", ".html", ".htm", ".js", ".json", ".jsonl", ".log", ".md",
    ".py", ".rst", ".text", ".txt", ".yaml", ".yml",
}


def extract_text(path: str | Path) -> tuple[str, str]:
    source_path = Path(path).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    suffix = source_path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(source_path))
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        return text, "pdf"

    if suffix not in TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported cabinet file type: {suffix or '(none)'}")

    text = source_path.read_text(encoding="utf-8", errors="replace")
    if suffix in {".html", ".htm"}:
        text = BeautifulSoup(text, "html.parser").get_text("\n")
        source_type = "html"
    else:
        source_type = suffix.lstrip(".") or "text"
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, source_type


def chunk_text(text: str, chunk_size: int = 2400, overlap: int = 240) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        if end < len(normalized):
            boundary = normalized.rfind("\n", start, end)
            if boundary <= start + chunk_size // 2:
                boundary = normalized.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(normalized[start:end].strip())
        if end >= len(normalized):
            break
        start = max(start + 1, end - overlap)
    return chunks


def ingest_paths(
    paths: Iterable[str | Path],
    store: CabinetStore | None = None,
) -> list[dict]:
    cabinet = store or CabinetStore()
    results = []
    for path in paths:
        text, source_type = extract_text(path)
        results.append(
            cabinet.index_document(path, text, source_type, chunk_text(text))
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Index explicit files into the local Conductor cabinet.")
    parser.add_argument("paths", nargs="+", help="Files to index; originals are never modified.")
    parser.add_argument("--db", dest="db_path", help="Optional SQLite database path.")
    args = parser.parse_args()
    store = CabinetStore(args.db_path)
    results = ingest_paths(args.paths, store=store)
    print(json.dumps({"results": results, "status": store.status()}, indent=2))


if __name__ == "__main__":
    main()
