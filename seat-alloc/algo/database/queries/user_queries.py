from algo.database.db import get_db

class UserQueries:
    @staticmethod
    def track_activity(user_id: int, endpoint: str):
        db = get_db()
        db.execute("""
            INSERT INTO user_activity (user_id, last_activity, last_endpoint)
            VALUES (?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                last_activity = CURRENT_TIMESTAMP,
                last_endpoint = excluded.last_endpoint
        """, (user_id, endpoint))
        db.commit()

    @staticmethod
    def get_user_activity(user_id: int):
        db = get_db()
        cursor = db.execute("SELECT * FROM user_activity WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
