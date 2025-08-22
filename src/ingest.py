# Author: Kartheek Nagelli
from __future__ import annotations
import pathlib, hashlib
import pandas as pd
from config import load_cfg
from utils.gcp import get_bq_client
from utils.data import list_local_docs, ensure_gcs_bucket
from logs import get_logger

def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def build_local_corpus_df():
    rows = []
    for p in list_local_docs():
        text = p.read_text(encoding="utf-8")
        rows.append({"doc_id": _hash(p.name + str(p.stat().st_mtime)), "filename": p.name, "text": text})
    return pd.DataFrame(rows)

def build_bq_public_df(cfg):
    bq = get_bq_client(cfg)
    job = bq.query(cfg.get("bq_public_query"))
    df = job.result().to_dataframe()
    return df[["doc_id","filename","text"]]

def main():
    cfg = load_cfg()
    log = get_logger("ingest")
    source = cfg.get("data_source","local")

    if source == "bq_public" and not cfg.get("local_mode"):
        df = build_bq_public_df(cfg)
        log.info(f"Loaded {len(df)} docs from BigQuery public dataset (BBC)")
    else:
        df = build_local_corpus_df()
        log.info(f"Loaded {len(df)} local docs")

    if not cfg.get("local_mode"):
        ensure_gcs_bucket(cfg)
        bq = get_bq_client(cfg)
        dataset_ref = bq.dataset(cfg["bq_dataset"])
        try:
            bq.get_dataset(dataset_ref)
        except Exception:
            bq.create_dataset(dataset_ref, exists_ok=True)
        table_id = f"{bq.project}.{cfg['bq_dataset']}.{cfg['bq_table_corpus']}"
        bq.load_table_from_dataframe(df, table_id).result()
        log.info(f"Loaded corpus into BigQuery: {table_id}")
    else:
        out = pathlib.Path(__file__).resolve().parents[1] / "artifacts"
        out.mkdir(exist_ok=True)
        try:
            df.to_parquet(out / "corpus.parquet")
            log.info("Saved local artifacts/corpus.parquet")
        except Exception:
            df.to_csv(out / "corpus.csv", index=False)
            log.info("Parquet not available; saved artifacts/corpus.csv")

if __name__ == "__main__":
    main()
