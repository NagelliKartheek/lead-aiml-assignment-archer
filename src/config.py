# Author: Kartheek Nagelli
from __future__ import annotations
import os, pathlib, yaml

CFG_PATH = pathlib.Path(__file__).resolve().parents[1] / "config.yaml"

def load_cfg() -> dict:
    with open(CFG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    if os.getenv("LOCAL_MODE") is not None:
        cfg["local_mode"] = os.getenv("LOCAL_MODE","true").lower() == "true"
    for k in ["project_id","location","gcs_bucket","gcs_prefix","bq_dataset","vertex_location"]:
        v = os.getenv(k.upper())
        if v:
            cfg[k] = v
    return cfg
