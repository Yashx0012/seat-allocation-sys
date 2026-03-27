import pytest
import time
import os
import hashlib
import hmac
import requests
from unittest.mock import patch

def test_rate_limiter():
    from core.rate_limit import FixedWindowRateLimiter
    
    limiter = FixedWindowRateLimiter(limit_per_minute=3)
    ip = "192.168.1.1"
    
    # First 3 should pass
    assert limiter.allow(ip) is True
    assert limiter.allow(ip) is True
    assert limiter.allow(ip) is True
    
    # 4th should block
    assert limiter.allow(ip) is False

def test_verify_signature_strips_prefix(mock_config):
    from core.cloud_sync import verify_signature
    mock_config.SYNC_SHARED_SECRET = "supersecret"
    
    payload = b'{"plan_id": "123"}'
    digest = hmac.new("supersecret".encode("utf-8"), payload, hashlib.sha256).hexdigest()
    
    # Test valid signature WITHOUT prefix
    assert verify_signature(payload, digest) is True
    
    # Test valid signature WITH prefix (our new fix!)
    assert verify_signature(payload, f"sha256={digest}") is True
    
    # Test invalid signatures
    assert verify_signature(payload, f"sha256=invalid") is False
    assert verify_signature(payload, f"sha256") is False
    assert verify_signature(payload, "") is False

def test_fetch_plan_enforces_size_limit(mock_config):
    from core.cloud_sync import _fetch_plan_content
    mock_config.SYNC_MAX_PAYLOAD_BYTES = 50 # Tiny limit
    
    # Mock a large response
    class MockResponse:
        def __init__(self, chunks):
            self.chunks = chunks
        def raise_for_status(self): pass
        def iter_content(self, chunk_size):
            for c in self.chunks:
                yield c
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
    with patch("requests.get") as mock_get:
        # Mock returns 100 bytes (2 chunks of 50), limit is 50. First chunk puts size at 50 (ok), 
        # second puts it at 100, which exceeds max_size.
        mock_get.return_value = MockResponse([b'A'*50, b'A'*50])
        
        with pytest.raises(ValueError, match="Payload exceeds maximum allowed size"):
            _fetch_plan_content({"object_url": "http://fake.com/big"})

def test_sync_queue_pragmas(tmp_path, monkeypatch):
    from core import sync_queue
    db_path = tmp_path / "test_pragmas.db"
    monkeypatch.setattr(sync_queue, "DB_PATH", db_path)
    
    # Initializing DB runs _conn() which has our PRAGMAS
    sync_queue.init_db()
    
    with sync_queue._conn() as con:
        j = con.execute("PRAGMA journal_mode").fetchone()
        assert j[0].upper() == "WAL", "WAL PRAGMA missing"
        
        s = con.execute("PRAGMA synchronous").fetchone()
        assert s[0] == 1, "synchronous=NORMAL PRAGMA missing" # 1 = NORMAL
        
        t = con.execute("PRAGMA temp_store").fetchone()
        assert t[0] == 2, "temp_store=MEMORY PRAGMA missing" # 2 = MEMORY
