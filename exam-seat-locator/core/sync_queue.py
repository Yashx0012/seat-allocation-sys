"""
core/sync_queue.py
Simple durable queue for cloud sync events backed by SQLite.
"""

import json
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sync_queue.db"


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=NORMAL")
    c.execute("PRAGMA temp_store=MEMORY")
    c.execute("PRAGMA cache_size=-10000")
    return c


def init_db() -> None:
    with _conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_jobs (
                event_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                attempts INTEGER NOT NULL DEFAULT 0,
                next_retry_at INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_sync_jobs_status_retry ON sync_jobs(status, next_retry_at)")


def enqueue(event_id: str, plan_id: str, payload: dict) -> bool:
    now = int(time.time())
    with _conn() as con:
        existing = con.execute("SELECT event_id FROM sync_jobs WHERE plan_id=? AND status='PENDING'", (plan_id,)).fetchone()
        if existing:
            return False
        try:
            con.execute(
                """
                INSERT INTO sync_jobs (event_id, plan_id, payload, status, attempts, next_retry_at, created_at, updated_at)
                VALUES (?, ?, ?, 'PENDING', 0, 0, ?, ?)
                """,
                (event_id, plan_id, json.dumps(payload), now, now),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def acquire_next() -> dict | None:
    now = int(time.time())
    with _conn() as con:
        row = con.execute(
            """
            SELECT * FROM sync_jobs
            WHERE status IN ('PENDING', 'FAILED') AND next_retry_at <= ?
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (now,),
        ).fetchone()
        if not row:
            return None

        con.execute(
            "UPDATE sync_jobs SET status='PROCESSING', updated_at=? WHERE event_id=?",
            (now, row['event_id']),
        )

        return {
            "event_id": row["event_id"],
            "plan_id": row["plan_id"],
            "payload": json.loads(row["payload"]),
            "attempts": row["attempts"],
        }


def mark_done(event_id: str) -> None:
    now = int(time.time())
    with _conn() as con:
        con.execute(
            "UPDATE sync_jobs SET status='DONE', updated_at=?, last_error=NULL WHERE event_id=?",
            (now, event_id),
        )


def mark_failed(event_id: str, attempts: int, error: str, max_attempts: int, base_backoff_sec: int) -> None:
    now = int(time.time())
    next_attempts = attempts + 1
    if next_attempts >= max_attempts:
        status = "DEAD"
        next_retry_at = now
    else:
        status = "FAILED"
        next_retry_at = now + (base_backoff_sec * (2 ** (next_attempts - 1)))

    with _conn() as con:
        con.execute(
            """
            UPDATE sync_jobs
            SET status=?, attempts=?, next_retry_at=?, last_error=?, updated_at=?
            WHERE event_id=?
            """,
            (status, next_attempts, next_retry_at, error[:1000], now, event_id),
        )
def delete_old_jobs(cutoff_time: int) -> int:
    with _conn() as con:
        cursor = con.execute(
            "DELETE FROM sync_jobs WHERE status IN ('DONE', 'DEAD') AND updated_at < ?",
            (cutoff_time,)
        )
        return cursor.rowcount

def recover_stuck_processing(timeout_seconds: int = 300, max_attempts: int = 6) -> int:
    now = int(time.time())
    cutoff = now - timeout_seconds
    
    with _conn() as con:
        rows = con.execute(
            "SELECT event_id, attempts FROM sync_jobs WHERE status='PROCESSING' AND updated_at < ?",
            (cutoff,)
        ).fetchall()
        
        recovered_count = 0
        for r in rows:
            eid = r["event_id"]
            attempts = r["attempts"]
            
            # Use mark_failed to handle backoff and DEAD states
            if attempts + 1 >= max_attempts:
                # Need custom DEAD logic because mark_failed doesn't return count
                con.execute(
                    "UPDATE sync_jobs SET status='DEAD', next_retry_at=?, updated_at=?, last_error='stuck_processing_aborted' WHERE event_id=?",
                    (now, now, eid)
                )
            else:
                next_retry = now  # Immediate retry for stuck
                con.execute(
                    "UPDATE sync_jobs SET status='FAILED', attempts=?, next_retry_at=?, updated_at=?, last_error='stuck_processing_recovered' WHERE event_id=?",
                    (attempts + 1, next_retry, now, eid)
                )
            recovered_count += 1
            
        return recovered_count

def cleanup_terminal(done_retention_seconds: int = 86400 * 7, dead_retention_seconds: int = 86400 * 14) -> int:
    now = int(time.time())
    done_cutoff = now - done_retention_seconds
    dead_cutoff = now - dead_retention_seconds
    with _conn() as con:
        cursor = con.execute(
            """
            DELETE FROM sync_jobs 
            WHERE (status = 'DONE' AND updated_at < ?)
               OR (status = 'DEAD' AND updated_at < ?)
            """,
            (done_cutoff, dead_cutoff)
        )
        return cursor.rowcount

def stats() -> dict:
    with _conn() as con:
        rows = con.execute(
            "SELECT status, COUNT(*) AS c FROM sync_jobs GROUP BY status"
        ).fetchall()
        retry_count = con.execute("SELECT COUNT(*) AS c FROM sync_jobs WHERE status='FAILED'").fetchone()[0]

    out = {"PENDING": 0, "PROCESSING": 0, "FAILED": 0, "DONE": 0, "DEAD": 0, "total_jobs": 0, "retry_jobs": retry_count, "fail_rate": 0.0}
    for r in rows:
        out[r["status"]] = r["c"]
        out["total_jobs"] += r["c"]
        
    if out["total_jobs"] > 0:
        out["fail_rate"] = out["FAILED"] / out["total_jobs"]
    return out
