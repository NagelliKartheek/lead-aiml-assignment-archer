# Author: Kartheek Nagelli
from __future__ import annotations
import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[0]

def run_step(name, path):
    print(f"\n=== {name} ===")
    r = subprocess.run([sys.executable, str(path)], check=True)
    return r.returncode

def main():
    run_step("Ingest", ROOT/"ingest.py")
    run_step("Preprocess", ROOT/"preprocess.py")
    run_step("Extract Entities", ROOT/"extract_entities.py")
    run_step("Summarize", ROOT/"summarize.py")
    run_step("Evaluate", ROOT/"evaluate.py")
    print("\nAgentic demo (local):")
    subprocess.run([sys.executable, str(ROOT/"agentic_workflow.py")], check=True)

if __name__ == "__main__":
    main()
