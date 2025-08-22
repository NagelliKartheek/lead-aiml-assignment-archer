# Author: Kartheek Nagelli
from __future__ import annotations
import pathlib, pandas as pd
from baselines import summarize_textrank, spacy_ner

def main():
    art = pathlib.Path(__file__).resolve().parents[1] / "src" / "artifacts"
    p_parq = art / "corpus_clean.parquet"
    p_csv = art / "corpus_clean.csv"
    df = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)
    rows = []
    for _, r in df.iterrows():
        text = r["text_clean"]
        rows.append({
            "doc_id": r["doc_id"],
            "filename": r["filename"],
            "textrank_summary": summarize_textrank(text, max_sentences=4),
            "spacy_entities": spacy_ner(text)
        })
    out = pd.DataFrame(rows)
    try:
        out.to_parquet(art / "baselines_eval.parquet")
    except Exception:
        out.to_csv(art / "baselines_eval.csv", index=False)
    print(f"Wrote {len(out)} baseline evaluations")
if __name__ == "__main__":
    main()
