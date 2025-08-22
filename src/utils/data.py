# Author: Kartheek Nagelli
from __future__ import annotations
import pathlib, typing as t
from .gcp import load_cfg, get_gcs_client

BASE = pathlib.Path(__file__).resolve().parents[2]
LOCAL_DOCS = BASE / "data" / "sample_docs"

def list_local_docs() -> t.List[pathlib.Path]:
    return sorted(LOCAL_DOCS.glob("*.txt"))

def ensure_gcs_bucket(cfg: dict):
    if cfg.get("local_mode"):
        return
    client = get_gcs_client(cfg)
    bucket = client.bucket(cfg["gcs_bucket"])
    if not bucket.exists():
        client.create_bucket(bucket)
    return bucket
