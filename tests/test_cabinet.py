import tempfile
import unittest
from pathlib import Path

from cabinet.ingest import ingest_paths
from cabinet.store import CabinetStore


class CabinetTests(unittest.TestCase):
    def test_indexes_searches_and_skips_unchanged_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "business-plan.txt"
            source.write_text(
                "The voice-first conductor uses a private searchable filing cabinet.",
                encoding="utf-8",
            )
            store = CabinetStore(root / "cabinet.sqlite3")

            first = ingest_paths([source], store=store)[0]
            second = ingest_paths([source], store=store)[0]
            results = store.search("voice conductor")

            self.assertEqual(first["status"], "indexed")
            self.assertEqual(second["status"], "unchanged")
            self.assertEqual(store.status()["documents"], 1)
            self.assertIn("voice-first conductor", results[0]["content"])

    def test_reindex_replaces_old_search_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "notes.md"
            store = CabinetStore(root / "cabinet.sqlite3")
            source.write_text("Legacy orange workflow", encoding="utf-8")
            ingest_paths([source], store=store)
            source.write_text("Current purple workflow", encoding="utf-8")
            ingest_paths([source], store=store)

            self.assertEqual(store.search("orange"), [])
            self.assertIn("purple", store.search("purple")[0]["content"])


if __name__ == "__main__":
    unittest.main()
