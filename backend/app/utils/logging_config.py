import logging
import sys
from app.utils.config import settings


def setup_logging() -> None:
    """Sets up unified logging for the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Configure specific third-party logger levels
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG and settings.ENVIRONMENT == "development" else logging.WARNING
    )

    logger = logging.getLogger("app")
    logger.info(f"Logging initialized with level: {logging.getLevelName(log_level)}")
