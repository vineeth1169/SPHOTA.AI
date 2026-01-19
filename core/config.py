"""
Configuration management for Sphota using pydantic-settings.

This module loads environment variables at startup and fails fast
if required settings are missing. It is safe to import from any
module; the Settings class defers reading environment until instantiation.
"""

from typing import List, Sequence, Any

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings loaded from environment or .env file."""

    # Required
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str

    # Optional with defaults
    LOG_LEVEL: str = "INFO"
    MODEL_PATH: str = "./models"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def _format_missing_errors(errors: Sequence[Any]) -> str:
    missing = []
    for err in errors:
        loc = getattr(err, "loc", None) if not isinstance(err, dict) else err.get("loc")
        err_type = getattr(err, "type", None) if not isinstance(err, dict) else err.get("type")
        if err_type == "missing":
            if isinstance(loc, (list, tuple)) and loc:
                missing.append(str(loc[0]))
            elif loc:
                missing.append(str(loc))
    if missing:
        return ", ".join(str(m) for m in missing if m)
    return "one or more required variables"


def load_settings() -> Settings:
    """Load settings and raise a clear error if required env vars are missing."""
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:  # pragma: no cover - startup fail-fast path
        missing_vars = _format_missing_errors(exc.errors())
        message = (
            f"Missing required environment variable(s): {missing_vars}. "
            "Please check your .env file."
        )
        raise RuntimeError(message) from exc


__all__ = ["Settings", "load_settings"]
