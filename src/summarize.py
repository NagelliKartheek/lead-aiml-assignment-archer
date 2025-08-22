# Author: Kartheek Nagelli
from __future__ import annotations
import pathlib, pandas as pd
from config import load_cfg
from utils.gcp import init_vertex
from logs import get_logger
try:
    from vertexai.generative_models import GenerativeModel
except Exception:
    GenerativeModel = None

SYS_PROMPT = """
Summarize the following document in 3-5 concise sentences. Write for a business stakeholder.
Capture key facts (who/what/when/results) and any noted risks/limitations.
"""

def vertex_summarize(text: str, model_name: str) -> str:
    model = GenerativeModel(model_name)
    resp = model.generate_content(f"{SYS_PROMPT}\n\nDocument:\n{text}")
    return resp.text.strip()

def heuristic_summarize(text: str) -> str:
    sents = [s.strip() for s in text.split('.') if s.strip()]
    return '. '.join(sents[:4]) + ('.' if sents else '')

def main():
    cfg = load_cfg()
    art = pathlib.Path(__file__).resolve().parents[1] / "artifacts"
    p_parq = art / "corpus_clean.parquet"
    p_csv = art / "corpus_clean.csv"
    df = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)

    summaries = []
    for _, row in df.iterrows():
        if cfg.get("local_mode") or GenerativeModel is None:
            summ = heuristic_summarize(row["text_clean"])
        else:
            init_vertex(cfg)
            summ = vertex_summarize(row["text_clean"], cfg.get("vertex_model_summary", "gemini-1.5-flash"))
        summaries.append({"doc_id": row["doc_id"], "filename": row["filename"], "summary": summ})

    try:
        out = pd.DataFrame(summaries)
        out.to_parquet(art/"summaries.parquet")
        from logs import get_logger
        log = get_logger("summarize")
        log.info(f"Wrote {len(out)} summaries -> artifacts/summaries.parquet")
    except Exception:
        out = pd.DataFrame(summaries)
        out.to_csv(art/"summaries.csv", index=False)
        from logs import get_logger
        log = get_logger("summarize")
        log.info(f"Parquet not available; wrote {len(out)} summaries -> artifacts/summaries.csv")

if __name__ == "__main__":
    main()
