# General utility functions and helper methods used across the backend application.
import json
from typing import Dict, Any, Optional

def parse_int_dict(val: Any) -> Dict[int, int]:
    """Parse a value into Dict[int, int]."""
    if isinstance(val, dict):
        return {int(k): int(v) for k, v in val.items()}
    if isinstance(val, str) and val:
        try:
            return json.loads(val)
        except Exception:
            pass
    return {}

def parse_str_dict(val: Any) -> Dict[int, str]:
    """Parse a value into Dict[int, str]."""
    if isinstance(val, dict):
        return {int(k): str(v) for k, v in val.items()}
    if isinstance(val, str) and val:
        try:
            return json.loads(val)
        except Exception:
            pass
    return {}
