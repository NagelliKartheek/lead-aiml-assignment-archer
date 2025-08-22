# Author: Kartheek Nagelli
from __future__ import annotations
import json, pathlib, pandas as pd
import re
from config import load_cfg
from utils.gcp import get_language_client, init_vertex
from logs import get_logger
try:
    from vertexai.generative_models import GenerativeModel
except Exception:
    GenerativeModel = None

PROMPT_TEMPLATE = """
You are a precise information extraction assistant. Given a document, extract:
- entities (person, org, location, date, money/percent if stated),
- key metrics (accuracy, uptime, latency if present),
- overall sentiment (positive/neutral/negative) with confidence 0-1,
- core issues/risks in a bullet list.

Return STRICT JSON with fields: entities{{type, text}}, metrics{{name, value}}, sentiment{{label, confidence}}, issues[].
Document:\n```{doc}```
"""

def extract_with_nl_api(client, text: str) -> dict:
    doc = {"content": text, "type_": 1}
    ent_resp = client.analyze_entities(request={"document": doc})
    sent_resp = client.analyze_sentiment(request={"document": doc})
    ents = []
    keep = {"PERSON","ORGANIZATION","LOCATION","DATE","PRICE","PERCENT"}
    for e in ent_resp.entities:
        t = e.type_.name
        if t in keep:
            ents.append({"type": t, "text": e.name})
    sent = sent_resp.document_sentiment
    return {
        "entities": ents,
        "sentiment": {"label": "positive" if sent.score>0.25 else "negative" if sent.score<-0.25 else "neutral", "confidence": min(1.0, abs(sent.score))}
    }

def extract_with_vertex(text: str) -> dict:
    cfg = load_cfg()
    init_vertex(cfg)
    model = GenerativeModel(cfg.get("vertex_model_extraction","gemini-1.5-pro"))
    out = model.generate_content(PROMPT_TEMPLATE.format(doc=text)).text
    try:
        return json.loads(out)
    except Exception:
        return {"raw": out}


def heuristic_extract(text: str) -> dict:
    # Simple keyword/regex-driven IE to work offline in local mode
    ents = []
    # Organizations / acronyms / capitalized sequences
    for m in re.finditer(r'\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+|\b[A-Z]{2,}\b|\b[A-Z]{2,}\s*\([A-Z]{2,}\))', text):
        t = m.group(0).strip()
        # Trim trailing punctuation
        t = t.strip(".,;:()")
        if len(t.split()) <= 6 and t.lower() not in {"the","and"}:
            ents.append({"type": "ORGANIZATION", "text": t})
    # Dates / months / quarters
    for m in re.finditer(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b|\bQ[1-4]\b', text, flags=re.I):
        ents.append({"type": "DATE", "text": m.group(0)})
    # Percentages / money
    for m in re.finditer(r'\b\d+(?:\.\d+)?\s*%|\$\s*\d+(?:\.\d+)?\b', text):
        ents.append({"type": "PERCENT", "text": m.group(0)})
    # Deduplicate by (type,text)
    seen = set()
    dedup = []
    for e in ents:
        key = (e["type"], e["text"])
        if key not in seen:
            seen.add(key)
            dedup.append(e)
    # Sentiment (very rough)
    pos_words = {"improved","expanded","positive","higher","better","reliable","support"}
    neg_words = {"concern","limitations","risk","crowding","cost","issue"}
    tokens = re.findall(r'[a-zA-Z]+', text.lower())
    pos = sum(t in pos_words for t in tokens)
    neg = sum(t in neg_words for t in tokens)
    score = (pos - neg) / max(1, (pos + neg))
    label = "positive" if score > 0.25 else "negative" if score < -0.25 else "neutral"
    conf = min(1.0, abs(score)) if (pos + neg) else 0.3
    # Issues/risk sentences
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    issues = [s for s in sents if re.search(r'\b(concern|issue|risk|limitation|requested|cost)\b', s, flags=re.I)]
    return {
        "entities": dedup[:20],
        "metrics": [{"name": "percent", "value": m["text"]} for m in dedup if m["type"] == "PERCENT"][:5],
        "sentiment": {"label": label, "confidence": round(float(conf), 2)},
        "issues": issues[:5]
    }


def main():
    cfg = load_cfg()
    log = get_logger("extract")
    art = pathlib.Path(__file__).resolve().parents[1] / "artifacts"
    p_parq = art / "corpus_clean.parquet"
    p_csv = art / "corpus_clean.csv"
    df = pd.read_parquet(p_parq) if p_parq.exists() else pd.read_csv(p_csv)

    results = []
    nl = get_language_client(cfg) if cfg.get("use_nl_api", True) and not cfg.get("local_mode") else None

    for _, row in df.iterrows():
        text = row["text_clean"]
        rec = {"doc_id": row["doc_id"], "filename": row["filename"]}
        if nl:
            rec["nl_api"] = extract_with_nl_api(nl, text)
        elif cfg.get("local_mode"):
            rec["heuristic"] = heuristic_extract(text)
        elif GenerativeModel is not None:
            rec["vertex_extraction"] = extract_with_vertex(text)
        results.append(rec)

    out = pathlib.DataFrame(results) if False else None  # keep variable for readability
    (art / "extractions.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    log.info(f"Wrote {len(results)} extractions to artifacts/extractions.json")

if __name__ == "__main__":
    main()
