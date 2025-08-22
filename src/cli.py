# Author: Kartheek Nagelli
from __future__ import annotations
import argparse, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[0]

def run_step(path: pathlib.Path) -> int:
    return subprocess.run([sys.executable, str(path)], check=True).returncode

def main():
    ap = argparse.ArgumentParser(description="NLP pipeline runner")
    ap.add_argument("cmd", choices=["all","ingest","preprocess","extract","summarize","evaluate","agent"], help="stage to run")
    args = ap.parse_args()

    if args.cmd in ("all","ingest"): run_step(ROOT/"ingest.py")
    if args.cmd in ("all","preprocess"): run_step(ROOT/"preprocess.py")
    if args.cmd in ("all","extract"): run_step(ROOT/"extract_entities.py")
    if args.cmd in ("all","summarize"): run_step(ROOT/"summarize.py")
    if args.cmd in ("all","evaluate"): run_step(ROOT/"evaluate.py")
    if args.cmd in ("all","agent"): run_step(ROOT/"agentic_workflow.py")

if __name__ == "__main__":
    main()
