import yaml
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from config.yaml with environment variable overrides."""
    config_path = Path(__file__).parent.parent / "config.yaml"

    if not config_path.exists():
        logger.error("config.yaml not found at %s", config_path)
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error("Failed to parse config.yaml: %s", e)
        sys.exit(1)

    # Override with environment variables if present
    config["llm"]["base_url"] = os.getenv("OLLAMA_BASE_URL", config["llm"]["base_url"])
    config["llm"]["model"] = os.getenv("OLLAMA_MODEL", config["llm"]["model"])
    config["chromadb"]["persist_directory"] = os.getenv(
        "CHROMA_PERSIST_DIR", config["chromadb"]["persist_directory"]
    )
    config["security"]["jwt_secret"] = os.getenv(
        "JWT_SECRET", config["security"].get("jwt_secret", "default-secret")
    )
    config["app"]["log_level"] = os.getenv(
        "LOG_LEVEL", config["app"].get("log_level", "INFO")
    )

    return config


CONFIG = load_config()
