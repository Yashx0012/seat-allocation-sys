import time
from typing import Dict

class FixedWindowRateLimiter:
    def __init__(self, limit_per_minute: int):
        self.limit = limit_per_minute
        self.window_size = 60
        self._counts: Dict[str, Dict[str, int]] = {}

    def allow(self, key: str) -> bool:
        if self.limit <= 0:
            return True
            
        current_time = int(time.time())
        window_key = str(current_time // self.window_size)
        
        # Cleanup old windows
        keys_to_delete = [w for w in self._counts.keys() if w != window_key]
        for w in keys_to_delete:
            del self._counts[w]
            
        if window_key not in self._counts:
            self._counts[window_key] = {}
            
        current_count = self._counts[window_key].get(key, 0)
        
        if current_count >= self.limit:
            return False
            
        self._counts[window_key][key] = current_count + 1
        return True


def get_client_ip(xff_header: str | None, remote_addr: str | None) -> str:
    if xff_header:
        return xff_header.split(',')[0].strip()
    return remote_addr or "unknown"
