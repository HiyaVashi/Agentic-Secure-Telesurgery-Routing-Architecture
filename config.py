<<<<<<< HEAD
from dotenv import load_dotenv
import os
from database.csv_database import CSVDatabase

csv_db = CSVDatabase()
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
=======
"""
config.py
─────────
Central configuration for the Agentic Telesurgery system.

This project compares different local language models using the
same agentic workflow.

Experimental Procedure:
    Run 1 → OLLAMA_MODEL = "llama3.2:3b"
    Run 2 → OLLAMA_MODEL = "vibethinker:1.5"

The workflow, prompts, datasets and agents remain identical.
Only the underlying LLM changes.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

# ------------------------------------------------------------------
# Project Root
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):

    # ==============================================================
    # OLLAMA SETTINGS
    # ==============================================================

    # Local Ollama server

    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # --------------------------------------------------------------
    # MODEL UNDER TEST
    #
    # Change ONLY this value when running experiments.
    #
    # Examples:
    #
    #   llama3.2:3b
    #   vibethinker:1.5
    #
    # Everything else in the workflow remains unchanged.
    # --------------------------------------------------------------

    OLLAMA_MODEL: str = "llama3.2:3b"

    OLLAMA_TEMPERATURE: float = 0.2

    # ==============================================================
    # DIRECTORY PATHS
    # ==============================================================

    PROMPTS_DIR: Path = BASE_DIR / "prompts"

    DATA_DIR: Path = BASE_DIR

    RESULTS_DIR: Path = BASE_DIR / "results"

    # ==============================================================
    # LOGGING
    # ==============================================================

    LOG_LEVEL: str = "INFO"

    LOG_FILE: str = "telesurgery.log"

    # ==============================================================
    # AGENT WEIGHTS
    # Paper: Equation (11)
    # ==============================================================

    WEIGHT_DOCTOR: float = 0.35

    WEIGHT_SECURITY: float = 0.30

    WEIGHT_PROTOCOL: float = 0.20

    WEIGHT_FEEDBACK: float = 0.15

    # ==============================================================
    # PROTOCOL SWITCHING
    # Paper: Algorithm 2
    # ==============================================================

    PACKET_LOSS_THRESHOLD_PCT: float = 5.0

    JITTER_THRESHOLD_MS: float = 100.0

    LATENCY_STABLE_MS: float = 30.0

    BACKUP_SERVER: str = "backup-satellite-node-01"

    # ==============================================================
    # TinyML Information
    # ==============================================================

    TINYML_ACCURACY: float = 0.94

    TINYML_MODEL_SIZE_KB: int = 550

    TINYML_TRAINING_UNITS: int = 85


    GOOGLE_CREDENTIALS: str = r"D:\Research\vol 2\credentials\google_credentials.json"

    SPREADSHEET_ID: str = "1dbdTY8QeFL5p1bDVDjBalMx_UjRejrP3MpYZOVVqVcE"

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
>>>>>>> a622173226c4d140cf54d90651d3ec0bdfa4d2dc
