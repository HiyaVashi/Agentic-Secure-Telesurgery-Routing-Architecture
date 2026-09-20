"""
models/ollama.py
────────────────
Local Ollama LLM Factory

Provides a configured ChatOllama instance for the Agentic
Telesurgery workflow.

Supported Models
----------------
• llama3.2:3b
• vibethinker:1.5

To switch experiments, simply change

    OLLAMA_MODEL

inside config.py.

Example
-------
Experiment 1

    OLLAMA_MODEL = "llama3.2:3b"

Experiment 2

    OLLAMA_MODEL = "vibethinker:1.5"

No other code changes are required.
"""

import subprocess

from langchain_ollama import ChatOllama

from config import settings
from utils.logger import setup_logger


logger = setup_logger("models.ollama")


def _check_model_exists(model_name: str) -> None:
    """
    Verify that the requested model exists locally in Ollama.

    Raises:
        RuntimeError
            If the model has not been pulled.
    """

    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )

        if model_name not in result.stdout:
            raise RuntimeError(
                f"Ollama model '{model_name}' is not installed.\n\n"
                f"Run:\n"
                f"    ollama pull {model_name}"
            )

    except FileNotFoundError:
        raise RuntimeError(
            "Ollama is not installed or is not available in PATH."
        )


def get_ollama_llm() -> ChatOllama:
    """
    Return a configured ChatOllama instance.
    """

    _check_model_exists(settings.OLLAMA_MODEL)

    logger.info(
        f"Using Ollama model: {settings.OLLAMA_MODEL}"
    )

    logger.info(
        f"Ollama server: {settings.OLLAMA_BASE_URL}"
    )

    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.OLLAMA_TEMPERATURE,
    )