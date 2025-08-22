from src.config import load_cfg

def test_load_cfg_has_defaults():
    cfg = load_cfg()
    assert "local_mode" in cfg
    assert "project_id" in cfg or cfg.get("local_mode") is True
