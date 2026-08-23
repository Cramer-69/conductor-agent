"""SQLite full-text filing cabinet that keeps source files in place."""

from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


_STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "can", "did",
    "does", "file", "files", "find", "for", "from", "have", "history",
    "how", "into", "latest", "look", "mine", "our", "please", "search",
    "show", "that", "the", "their", "then", "there", "these", "this",
    "through", "what", "when", "where", "which", "with", "would", "you",
    "your",
}


class CabinetStore:
    """Index and search local documents without moving or uploading them."""

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent / "data" / "cabinet" / "cabinet.sqlite3"
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    path TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    modified_at REAL NOT NULL,
                    sha256 TEXT NOT NULL,
                    indexed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY,
                    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    UNIQUE(document_id, chunk_index)
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    title,
                    path UNINDEXED,
                    source_type UNINDEXED,
                    content,
                    tokenize = 'porter unicode61'
                );
                """
            )

    @property
    def enabled(self) -> bool:
        return self.status()["documents"] > 0

    def status(self) -> dict[str, Any]:
        with self._connect() as connection:
            documents = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunks = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            latest = connection.execute("SELECT MAX(indexed_at) FROM documents").fetchone()[0]
        return {
            "documents": documents,
            "chunks": chunks,
            "last_indexed_at": latest,
            "database": str(self.db_path),
            "local_only": True,
        }

    def index_document(
        self,
        path: str | Path,
        text: str,
        source_type: str,
        chunks: Iterable[str],
    ) -> dict[str, Any]:
        source_path = Path(path).expanduser().resolve()
        stat = source_path.stat()
        digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
        indexed_at = datetime.now(timezone.utc).isoformat()
        title = source_path.stem.replace("_", " ").replace("-", " ").strip() or source_path.name
        prepared_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id, sha256 FROM documents WHERE path = ?",
                (str(source_path),),
            ).fetchone()
            if existing and existing["sha256"] == digest:
                count = connection.execute(
                    "SELECT COUNT(*) FROM chunks WHERE document_id = ?",
                    (existing["id"],),
                ).fetchone()[0]
                return {"path": str(source_path), "chunks": count, "status": "unchanged"}

            if existing:
                row_ids = connection.execute(
                    "SELECT id FROM chunks WHERE document_id = ?",
                    (existing["id"],),
                ).fetchall()
                connection.executemany(
                    "DELETE FROM chunks_fts WHERE rowid = ?",
                    ((row["id"],) for row in row_ids),
                )
                connection.execute("DELETE FROM documents WHERE id = ?", (existing["id"],))

            cursor = connection.execute(
                """
                INSERT INTO documents (
                    path, title, source_type, size_bytes, modified_at, sha256, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(source_path),
                    title,
                    source_type,
                    stat.st_size,
                    stat.st_mtime,
                    digest,
                    indexed_at,
                ),
            )
            document_id = cursor.lastrowid
            for chunk_index, content in enumerate(prepared_chunks):
                chunk_cursor = connection.execute(
                    "INSERT INTO chunks (document_id, chunk_index, content) VALUES (?, ?, ?)",
                    (document_id, chunk_index, content),
                )
                connection.execute(
                    """
                    INSERT INTO chunks_fts (rowid, title, path, source_type, content)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (chunk_cursor.lastrowid, title, str(source_path), source_type, content),
                )

        return {"path": str(source_path), "chunks": len(prepared_chunks), "status": "indexed"}

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        terms = [
            token.lower()
            for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", query)
            if token.lower() not in _STOP_WORDS
        ]
        unique_terms = list(dict.fromkeys(terms))[:12]
        if not unique_terms:
            return []
        fts_query = " OR ".join(f'"{term.replace(chr(34), "")}"' for term in unique_terms)

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    chunks_fts.title,
                    chunks_fts.path,
                    chunks_fts.source_type,
                    snippet(chunks_fts, 3, '[', ']', ' ... ', 36) AS snippet,
                    chunks.content,
                    bm25(chunks_fts, 3.0, 0.0, 0.0, 1.0) AS rank
                FROM chunks_fts
                JOIN chunks ON chunks.id = chunks_fts.rowid
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (fts_query, max(1, min(limit, 20))),
            ).fetchall()

        return [
            {
                "title": row["title"],
                "path": row["path"],
                "source_type": row["source_type"],
                "snippet": row["snippet"],
                "content": row["content"],
                "score": row["rank"],
            }
            for row in rows
        ]
