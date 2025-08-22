# Author: Kartheek Nagelli
from __future__ import annotations
import re, pandas as pd, pathlib
from config import load_cfg
from logs import get_logger

CLEAN_RE = re.compile(r"\s+", re.MULTILINE)

def clean_text(s: str) -> str:
    s = s.strip()
    s = CLEAN_RE.sub(" ", s)
    return s

def basic_eda(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "n_docs": [len(df)],
        "avg_len": [df["text"].str.len().mean()],
        "median_len": [df["text"].str.len().median()],
    })

def main():
    cfg = load_cfg()
    log = get_logger("preprocess")
    art = pathlib.Path(__file__).resolve().parents[1] / "artifacts"
    p_parq = art / "corpus.parquet"
    p_csv = art / "corpus.csv"
    df = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)
    df["text_clean"] = df["text"].map(clean_text)
    eda = basic_eda(df)
    log.info("\n" + eda.to_string(index=False))
    try:
        df.to_parquet(art / "corpus_clean.parquet")
        log.info("Saved artifacts/corpus_clean.parquet")
    except Exception:
        df.to_csv(art / "corpus_clean.csv", index=False)
        log.info("Parquet not available; saved artifacts/corpus_clean.csv")

if __name__ == "__main__":
    main()
