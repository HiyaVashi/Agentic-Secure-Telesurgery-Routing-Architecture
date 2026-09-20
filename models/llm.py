"""
models/llm.py
─────────────
Central LLM Factory

This module provides the language model used by every AI agent
(Doctor, Security, Protocol, Feedback, Backup).

Research Methodology
--------------------
The workflow, prompts, datasets, and agent architecture remain
identical throughout all experiments.

The ONLY experimental variable is the language model specified in
config.py.

Example:

Experiment 1
------------
OLLAMA_MODEL = "llama3.2:3b"

Experiment 2
------------
OLLAMA_MODEL = "vibethinker:1.5"

No other code changes are required.
"""

from langchain_core.language_models import BaseLanguageModel

from config import settings
from models.ollama import get_ollama_llm
from utils.logger import setup_logger


logger = setup_logger("models.llm")


def get_llm() -> BaseLanguageModel:
    """
    Return the configured Ollama language model.

    Every agent receives the same model instance.
    The model is selected through config.py.
    """

    logger.info("=" * 60)
    logger.info("Initialising Language Model")
    logger.info(f"Model      : {settings.OLLAMA_MODEL}")
    logger.info(f"Temperature: {settings.OLLAMA_TEMPERATURE}")
    logger.info("=" * 60)

    return get_ollama_llm()