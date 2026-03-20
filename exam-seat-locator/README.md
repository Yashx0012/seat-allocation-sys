# Exam Seat Locator

Lightweight Flask app for students to find their assigned exam seat.
Enter roll number + exam date + time slot -> see classroom grid with your seat highlighted.

---

## Project Structure

```
exam-seat-locator/
├── app.py                   # Routes: /, /search, /upload, /reload
├── config.py                # DATA_DIR, SECRET_KEY, HOST, PORT, ALLOWED_EXTENSIONS,
│                            #   PLAN_RETENTION_DAYS, CLEANUP_INTERVAL_DAYS
├── requirements.txt
├── core/
│   ├── __init__.py          # Exports AppCache singleton (cache.load() on startup)
│   ├── cache.py             # AppCache — owns _index + _lru, coordinates all lookups
│   ├── lru_cache.py         # Thread-safe LRU (OrderedDict, maxsize=5)
│   ├── plan_index.py        # Builds/loads summary_index.json (roll -> filename map)
│   ├── extractor.py         # Turns raw PLAN dict -> list of room sessions
│   ├── indexer.py           # Builds O(1) student_index + session_index
│   ├── loader.py            # Reads PLAN-*.json from disk, parses dates
│   ├── matrix.py            # Builds 2-D seat grid from room config + students
│   ├── cleanup.py           # Daemon thread — removes PLAN files older than PLAN_RETENTION_DAYS
│   ├── cloud_sync.py        # Webhook handler, HMAC verification, background worker for S3/R2 downloads
│   ├── sync_queue.py        # SQLite queue for tracking webhook jobs with heartbeat/recovery
│   ├── rate_limit.py        # Fixed-window memory-based rate limiting for API endpoints
│   └── backend_sync.py      # Direct file sync for single-VM/local setups
├── data/                    # PLAN-*.json files + summary_index.json (auto-generated)
├── templates/
│   ├── index.html           # Search form — date/time from dynamic dropdowns
│   └── result.html          # Classroom grid + click-to-open seat info card
├── static/
│   └── style.css            # Dark/light theme, seat tiles, info card styles
└── data/summary_index.json  # Auto-generated roll → filename map (rebuilt on /reload)
```

---

## Setup & Run

```bash
pip install -r requirements.txt

# Drop one or more PLAN-*.json files into data/
python app.py
# -> http://127.0.0.1:5000
```

> **Retention period** — edit `PLAN_RETENTION_DAYS` and `CLEANUP_INTERVAL_DAYS` in `config.py`
> to change how long plan files are kept and how often the daemon scans.

---

## How It Works

1. On startup `AppCache.load()` scans `data/PLAN-*.json`, builds `summary_index.json`
2. Top-3 most-hit plan files are pre-warmed into the LRU
3. Cleanup daemon starts immediately — deletes any plan file older than `PLAN_RETENTION_DAYS` days, then sleeps for `CLEANUP_INTERVAL_DAYS` days and repeats
4. Student searches: roll number -> `_index` (O(1)) -> filename -> LRU hit or disk read -> seat
5. Result page renders classroom grid; clicking your seat opens a detail card

---

## Adding New Plan Files

- Drop a new `PLAN-*.json` into `data/` and hit `POST /reload`, **or**
- Use the upload button on the home page — index rebuilds automatically, no restart needed

---

## Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Search form with dynamic date/time dropdowns (shows only non-stale dates) |
| `/search` | POST | Look up seat by roll number + date + time |
| `/upload` | POST | Upload a new `PLAN-*.json` file |
| `/reload` | POST | Rebuild index + clear LRU; returns stats JSON |
| `/api/sync/notify` | POST | Cloud webhook receiver for published S3/R2 plans (HMAC-verified) |
| `/api/sync/stats` | GET | Check lag, retry metrics, and worker queue health |

---

## Reliability & Performance Improvements

- **Debounced Re-indexing:** A `_ReloadBatcher` intercepts webhook mass-downloads, grouping cache rebuilds to prevent high CPU overhead during bulk plan syncing.
- **Queue Heartbeat & Recovery:** `sync_queue` runs a native heartbeat that detects and aborts jobs stuck in `PROCESSING` over a specific timeout to ensure queue integrity.
- **Memory Safety:** `cloud_sync` employs 8KB chunk-streaming constraints to prevent large `PLAN-*.json` downloads from creating Out-Of-Memory (OOM) failures.
- **API Guardrails:** Endpoints are protected by a native, dictionary-based `FixedWindowRateLimiter`.
- **Database Concurrency:** The SQLite webhook task queue operates in `WAL` journaling with memory temp storage to completely eliminate "database is locked" bottlenecks under burst loads.

---

## Architecture

- **`AppCache`** — singleton loaded once at startup; no per-request I/O on warm paths
- **`LRUCache`** — thread-safe, `maxsize=5`; evicts least-recently-used plan on overflow
- **`summary_index.json`** — maps every roll number -> list of filenames; fits in L2 cache (~200KB)
- **`student_index`** — `(roll, date, start, end)` -> `{room, session, row, col}` — O(1) lookup
- **`matrix.py`** — stores `position` (e.g. `B5`) in every cell for grid-ref display
- **`cleanup.py`** — daemon thread (`daemon=True`); first run immediately at startup, then every `CLEANUP_INTERVAL_DAYS` days; calls `cache.reload()` after any deletion

### Adjusting retention

All cleanup timing is controlled by two constants in `config.py` — change them once and every part of the system picks up the new value automatically:

```python
PLAN_RETENTION_DAYS   = 15   # delete files older than this
CLEANUP_INTERVAL_DAYS = 15   # how often the daemon wakes up
```

---

## Performance

| Scenario | Time |
|---|---|
| Warm search (LRU hit) | ~4-9ms |
| Cold search (LRU miss) | ~80-190ms (one-time NVMe read) |
| Info card open | <1ms JS + 300ms animation |
| RAM footprint (788 students, 3 files) | ~65MB |
