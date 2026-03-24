import logging
import os
from logging.config import dictConfig


def setup_logger():
    os.makedirs("logs", exist_ok=True)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "logs/app.log",
                "encoding": "utf-8",
                "formatter": "default",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    })


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)