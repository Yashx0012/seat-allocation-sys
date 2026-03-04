"""
config.py - Central configuration for Exam Seat Locator.
All path constants and app-level settings live here.
"""

import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
# PLAN_FILE removed — the system now supports multiple plan files.
# The summary index (data/summary_index.json) maps roll numbers → filenames.

# ── Flask ────────────────────────────────────────────────────────────────────────────
SECRET_KEY  = "exam-seat-locator-secret-key-2026"
DEBUG       = False
HOST        = "0.0.0.0"
PORT        = 5000

# Allowed extensions for plan file uploads
ALLOWED_EXTENSIONS = {"json"}
