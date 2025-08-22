# Intelligent Data Extraction & Summarization on GCP (Agentic)

This repository contains a compact, production‑minded NLP pipeline that ingests unstructured text,
extracts key information (entities, sentiment, issues), generates concise stakeholder summaries,
and demonstrates a simple agentic workflow (planner + tools: search → summarize).

- **Public dataset (GCP)**: `bigquery-public-data.bbc_news.fulltext`
- **Local quick‑start**: small `.txt` files in `data/sample_docs`
- **Outputs**: artifacts in `artifacts/` (at runtime) and sample CSV in `outputs/`
- **Extras**: Dockerfile, Makefile, pytest tests, requirements checker, architecture report (Word) + diagram

---

## Quick Start (Local)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pip install pytest

# Run the whole pipeline
python -m src.cli all

# (Optional) run tests
pytest -q
```

Artifacts will be written to `artifacts/` (ignored by git). A sample combined output from a local run is at:
`outputs/local_outputs_entities_summaries_*.csv`.

---

## Quick Start (GCP with BigQuery Public Dataset)
1. Edit `config.yaml`:
   ```yaml
   local_mode: false
   data_source: bq_public
   project_id: <YOUR_GCP_PROJECT_ID>
   ```
2. Authenticate & enable services:
   ```bash
   gcloud auth application-default login
   gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com language.googleapis.com storage.googleapis.com
   ```
3. Run stages:
   ```bash
   python src/ingest.py
   python src/preprocess.py
   python src/extract_entities.py
   python src/summarize.py
   python src/evaluate.py
   python src/agentic_workflow.py
   ```
4. Verify outputs in **BigQuery** (dataset from `config.yaml`):
   - `<project>.<bq_dataset>.documents`
   - `<project>.<bq_dataset>.extracted_entities`
   - `<project>.<bq_dataset>.summaries`

> Summarization can use Vertex AI in GCP mode; in local mode, a deterministic heuristic is used to keep runs offline.

---

## Configuration (snippet)
```yaml
project_id: YOUR_GCP_PROJECT_ID
location: us-central1
gcs_bucket: archer-nlp-demo-bucket
bq_dataset: nlp_demo

# Execution
local_mode: true        # flip to false for GCP
data_source: local      # set to bq_public for BigQuery Public Dataset

# Public dataset query (BBC)
bq_public_query: |
  WITH base AS (
    SELECT ANY_VALUE(title) AS title, content
    FROM `bigquery-public-data.bbc_news.fulltext`
    WHERE content IS NOT NULL
    GROUP BY content
  )
  SELECT
    TO_HEX(MD5(content))                         AS doc_id,
    CONCAT('bbc_', TO_HEX(MD5(content)), '.txt') AS filename,
    CONCAT(IFNULL(title, ''), '\n\n', content) AS text
  FROM base
  LIMIT 500
```

---

## Project Structure
```
src/
  ingest.py           # Ingest from local or BigQuery Public Datasets
  preprocess.py       # Cleanup + EDA
  extract_entities.py # Entities, sentiment, issues (NL API / Vertex / local heuristic)
  summarize.py        # 3–5 sentence summaries (Vertex / heuristic)
  evaluate.py         # Length stats, optional ROUGE
  agentic_workflow.py # Simple planner + tools (search → summarize)
  utils/
    gcp.py, data.py
  cli.py, config.py, logs.py

data/sample_docs/     # Local quick-start inputs
tests/                # pytest unit tests
tools/req_checker.py  # Requirements checker
outputs/              # Example combined outputs (CSV)
```

---

## Agentic Workflow (at a glance)
- Planner inspects the query and decides which tool(s) to call.
- Typical path: **search_corpus → summarize** (returns top matches with summaries).
- Tools are modular Python functions that can be moved behind Cloud Run endpoints later.

---

## Dataset Provenance
- **Public**: `bigquery-public-data.bbc_news.fulltext`
- We generate `doc_id` from `MD5(content)`, construct a filename, and set `text = title + content` for consistent downstream processing.
- See `DATA_PROVENANCE.txt` for details.

---

## Docker / Makefile
```bash
# Build and run with Docker (local mode)
docker build -t nlp-agentic:latest .
docker run --rm nlp-agentic:latest
```
```bash
# Makefile shortcuts
make install     # install deps + pytest
make run         # python -m src.cli all
make test        # pytest -q
```

---

## Tests
```bash
pytest -q
```

---

## Requirement Checker
```bash
python tools/req_checker.py
```
The checker verifies presence of code/docs, config keys (`local_mode`, `data_source`, BBC SQL), and optional tooling.

---

Prepared on 2025-08-22.
