"""
core/loader.py - Disk I/O layer.
Only this module ever touches the filesystem.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def load_plan_file(plan_path: str) -> dict | None:
    """
    Read and parse the master PLAN JSON file from disk.
    Returns the parsed dict, or None on any error.
    This is the ONLY place a file is read — called once at startup/reload.
    """
    if not os.path.exists(plan_path):
        logger.error(f"NOT FOUND  {plan_path}")
        return None

    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"READ  {os.path.basename(plan_path)}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON ERR  {os.path.basename(plan_path)}: {e}")
        return None
    except IOError as e:
        logger.error(f"IO ERR  {os.path.basename(plan_path)}: {e}")
        return None


def convert_date_format(date_str: str) -> str:
    """Convert 'MM-DD-YYYY' → 'YYYY-MM-DD'."""
    try:
        return datetime.strptime(date_str, "%m-%d-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str
