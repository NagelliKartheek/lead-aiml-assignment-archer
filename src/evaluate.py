# Author: Kartheek Nagelli
from __future__ import annotations
import pathlib, pandas as pd
from config import load_cfg
from logs import get_logger

try:
    from rouge_score import rouge_scorer
except Exception:
    rouge_scorer = None

def main():
    cfg = load_cfg()
    log = get_logger("evaluate")
    art = pathlib.Path(__file__).resolve().parents[1] / "artifacts"
    p_parq = art / "summaries.parquet"
    p_csv = art / "summaries.csv"
    sums = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)
    sums["len_chars"] = sums["summary"].str.len()
    log.info("Summary length stats:\n" + str(sums["len_chars"].describe()))

    ref_path = art / "references.parquet"
    if ref_path.exists() and rouge_scorer is not None:
        refs = pd.read_parquet(ref_path)
        df = sums.merge(refs, on="doc_id", how="inner")
        scorer = rouge_scorer.RougeScorer(["rouge1","rougeL"], use_stemmer=True)
        scores = [scorer.score(r["reference"], r["summary"]) for _, r in df.iterrows()]
        log.info("Sample ROUGE: " + str(scores[:3]))

if __name__ == "__main__":
    main()
