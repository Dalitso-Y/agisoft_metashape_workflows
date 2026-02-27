from __future__ import annotations
import os
import sys

# Add repo scripts/ to sys.path
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from run_workflow import run

CONFIG = os.path.join(THIS_DIR, "config.json")
run(CONFIG, workflow_name="aerial_rtk_no_gcps")