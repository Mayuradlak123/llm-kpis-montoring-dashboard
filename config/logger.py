import logging
from logging.config import dictConfig
import os
from pydantic import BaseModel
os.makedirs("logs", exist_ok=True)

class RelativePathFilter(logging.Filter):
    """Filter to inject relative path into log records."""
    def filter(self, record):
        try:
            # Get relative path from current working directory
            record.relpath = os.path.relpath(record.pathname, os.getcwd())
        except Exception:
            record.relpath = record.filename
        return True

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "relative_path": {
            "()": RelativePathFilter,
        }
    },
    "formatters": {
        "console": {
            "format": "%(levelname)s: %(asctime)s - [%(relpath)s:%(lineno)d] - %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "file": { 
            "format": "%(levelname)s: %(asctime)s - [%(relpath)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "formatter": "console",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "filters": ["relative_path"]
        },
        "file": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": "logs/llm_kpi_monitoring.log",
            "mode": "a",
            "encoding": "utf-8",
            "filters": ["relative_path"]
        },
    },
    "loggers": {
        "llm-kpi-monitoring": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    }
}

dictConfig(log_config)
logger = logging.getLogger("llm-kpi-monitoring")