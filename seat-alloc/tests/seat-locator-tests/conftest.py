import pytest
import os
from pathlib import Path
import tempfile
import sys
import importlib
import time

@pytest.fixture(autouse=True)
def setup_path():
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "exam-seat-locator"))

@pytest.fixture
def mock_config(monkeypatch):
    import config
    monkeypatch.setattr(config, "DATA_DIR", tempfile.mkdtemp())
    monkeypatch.setattr(config, "SYNC_WORKER_POLL_SECONDS", 0.01)
    return config


