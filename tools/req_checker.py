import json, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
cfg = ROOT / "config.yaml"
readme = ROOT / "README_PLAIN.txt"
prov = ROOT / "DATA_PROVENANCE.txt"
src = ROOT / "src"
tests = ROOT / "tests"

requirements = {
  "code_files": ["ingest.py","preprocess.py","extract_entities.py","summarize.py","evaluate.py","agentic_workflow.py","cli.py","config.py","logs.py"],
  "utils": ["gcp.py","data.py"],
  "docs": ["README_PLAIN.txt","DATA_PROVENANCE.txt","ARCHITECTURE_REPORT_PLAIN.txt"],
  "tests": ["test_preprocess.py","test_agentic.py","test_config.py"]
}

def check_presence():
    missing = []
    for f in requirements["docs"]:
        if not (ROOT / f).exists():
            missing.append(f)
    for f in requirements["code_files"]:
        if not (src / f).exists():
            missing.append("src/" + f)
    for f in requirements["utils"]:
        if not (src / "utils" / f).exists():
            missing.append("src/utils/" + f)
    for f in requirements["tests"]:
        if not (tests / f).exists():
            missing.append("tests/" + f)
    return missing

def check_config():
    if not cfg.exists():
        return {"present": False}
    t = cfg.read_text(encoding="utf-8")
    has_local = "local_mode" in t
    has_source = "data_source" in t
    has_bbc = "bigquery-public-data.bbc_news.fulltext" in t
    return {"present": True, "local_mode_defined": has_local, "data_source_defined": has_source, "bbc_query_present": has_bbc}

def check_readme():
    if not readme.exists():
        return {"present": False}
    t = readme.read_text(encoding="utf-8").lower()
    notes = {
      "has_data_sources": "data sources" in t,
      "mentions_bbc": "bbc" in t and "fulltext" in t,
      "has_run_steps": "how to run" in t or "run stages" in t,
    }
    return {"present": True, **notes}

def check_optional():
    docker = (ROOT / "Dockerfile").exists()
    make = (ROOT / "Makefile").exists()
    pyproj = (ROOT / "pyproject.toml").exists()
    sec = (ROOT / "SECURITY.txt").exists()
    contrib = (ROOT / "CONTRIBUTING.txt").exists()
    return {"dockerfile": docker, "makefile": make, "pyproject": pyproj, "security": sec, "contributing": contrib}

def main():
    out = {
      "missing_files": check_presence(),
      "config": check_config(),
      "readme": check_readme(),
      "optional": check_optional()
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
