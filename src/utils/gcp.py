# Author: Kartheek Nagelli
from __future__ import annotations
import pathlib, yaml
try:
    from google.cloud import storage
    from google.cloud import bigquery
    from google.cloud import language_v1 as language
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
except Exception:
    storage = bigquery = language = vertexai = GenerativeModel = Part = None

CFG_PATH = pathlib.Path(__file__).resolve().parents[2] / "config.yaml"

def load_cfg() -> dict:
    with open(CFG_PATH, "r") as f:
        return yaml.safe_load(f)

def init_vertex(cfg: dict):
    if cfg.get("local_mode"):
        return None
    if vertexai is None:
        raise RuntimeError("vertexai SDK not installed")
    vertexai.init(project=cfg["project_id"], location=cfg["vertex_location"])

def get_gcs_client(cfg: dict):
    if cfg.get("local_mode"):
        return None
    if storage is None:
        raise RuntimeError("google-cloud-storage not installed")
    return storage.Client(project=cfg["project_id"])

def get_bq_client(cfg: dict):
    if cfg.get("local_mode"):
        return None
    if bigquery is None:
        raise RuntimeError("google-cloud-bigquery not installed")
    return bigquery.Client(project=cfg["project_id"])

def get_language_client(cfg: dict):
    if cfg.get("local_mode"):
        return None
    if language is None:
        raise RuntimeError("google-cloud-language not installed")
    return language.LanguageServiceClient()
