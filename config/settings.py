import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PRIMARY_REPO_DIR = BASE_DIR/"data"/"primary_repo"
EVALUATION_REPO_DIR = BASE_DIR/"data"/"evaluation_repo"

SUPPORTED_EXTENSIONS = [".txt" , ".md"]