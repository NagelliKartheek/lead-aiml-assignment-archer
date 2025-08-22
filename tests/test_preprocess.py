import pandas as pd
from src.preprocess import clean_text, basic_eda

def test_clean_text_compacts_spaces():
    s = " line1\n\nline2\t\tline3  "
    out = clean_text(s)
    assert "  " not in out
    assert out.startswith("line1") and out.endswith("line3")

def test_basic_eda_counts():
    df = pd.DataFrame({ "text": ["a","bb","ccc"] })
    stats = basic_eda(df)
    assert stats.loc[0,"n_docs"] == 3
    assert int(stats.loc[0,"avg_len"]) >= 1
