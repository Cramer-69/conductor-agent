"""
Logging utilities for the Conductor Agent.
Provides structured logging with rich console output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from config.settings import settings


# Rich console for beautiful output
console = Console()


def setup_logger(name: str = "conductor_agent") -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Rich console handler
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_time=False,
        show_path=False
    )
    console_handler.setLevel(logging.INFO)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def log_processing_stats(processor_name: str, **stats):
    """Log processing statistics in a formatted way."""
    logger.info(f"[bold blue]{processor_name}[/bold blue] Processing Stats:", extra={"markup": True})
    for key, value in stats.items():
        logger.info(f"  • {key}: {value}")


def describe_integrations(**tools) -> str:
    """Summarize which optional integrations came up enabled.

    Each tool exposes an `enabled` property that is False when its API key is
    absent, in which case the tool no-ops instead of raising. Reporting the
    state at startup keeps a missing key from looking like a working feature
    that simply never remembers or finds anything.
    """
    return " ".join(
        f"{name}={'on' if getattr(tool, 'enabled', False) else 'OFF (no key)'}"
        for name, tool in tools.items()
    )
