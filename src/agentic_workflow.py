# Author: Kartheek Nagelli
from __future__ import annotations
import re, json, pathlib, pandas as pd

def search_corpus_local(term: str, art_dir: pathlib.Path):
    p_parq = art_dir / "corpus_clean.parquet"
    p_csv = art_dir / "corpus_clean.csv"
    df = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)
    mask = df["text_clean"].str.contains(term, case=False, regex=False) | df["filename"].str.contains(term, case=False, regex=False)
    return df[mask].to_dict(orient="records")

def summarize_local(doc_id: str, art_dir: pathlib.Path):
    p_parq = art_dir / "summaries.parquet"
    p_csv = art_dir / "summaries.csv"
    s = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)
    row = s.loc[s["doc_id"] == doc_id]
    return None if row.empty else row.iloc[0]["summary"]

def plan(query: str) -> list:
    q = query.lower()
    steps = []
    if any(k in q for k in ["find","show","which","where","sentiment","entity","issue"]):
        steps.append({"tool":"search_corpus","args":{"term": re.sub(r"[^a-z0-9 ]","", q).split()[-1]}})
        steps.append({"tool":"summarize","args":{}})
    else:
        steps.append({"tool":"summarize","args":{}})
    return steps

def run(query: str):
    art = pathlib.Path(__file__).resolve().parents[1] / "artifacts"
    steps = plan(query)
    candidates = []

    for step in steps:
        if step["tool"] == "search_corpus":
            term = step["args"].get("term", "")
            candidates = search_corpus_local(term, art)
        elif step["tool"] == "summarize" and candidates:
            for c in candidates:
                c["summary"] = summarize_local(c["doc_id"], art)
    return {"query": query, "plan": steps, "results": candidates[:3]}

if __name__ == "__main__":
    out = run("Find issues in transit report")
    print(json.dumps(out, indent=2))
