# Local filing cabinet

The cabinet is a private SQLite full-text index. Source files stay where they
are; ingestion reads them and stores searchable text chunks under
`data/cabinet/`, which Git ignores.

Index only files you intentionally select:

```bash
.venv/bin/python -m cabinet.ingest "/absolute/path/to/file.pdf" "/absolute/path/to/export.json"
```

Search through the Conductor API:

```bash
curl -sS -H 'Content-Type: application/json' \
  -d '{"query":"voice conductor plan","limit":5}' \
  http://127.0.0.1:8080/api/cabinet/search
```

Or speak naturally through the Conductor, for example: “Search my filing
cabinet for the voice plan.” Matching excerpts are supplied to the active AI
provider as reference material. The raw source documents are never moved or
uploaded by the ingestion process.
