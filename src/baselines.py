# Author: Kartheek Nagelli
from __future__ import annotations
import warnings

def summarize_textrank(text: str, max_sentences: int = 4) -> str:
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.text_rank import TextRankSummarizer
    except Exception:
        warnings.warn("sumy not installed; falling back to naive summarizer")
        sents = [s.strip() for s in text.split('.') if s.strip()]
        return '. '.join(sents[:max_sentences]) + ('.' if sents else '')
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    sentences = summarizer(parser.document, max_sentences)
    return ' '.join(str(s) for s in sentences)

def spacy_ner(text: str):
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        warnings.warn("spaCy or model not installed; returning empty entities")
        return []
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
