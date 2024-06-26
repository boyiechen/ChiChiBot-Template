import sqlite3
from icecream import ic
# from config import SQLITE_DB_PATH

class EventManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def create_event(self, title, description, event_date, location, group_id, user_ids):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO events (title, description, event_date, location, group_id, user_ids)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, event_date, location, group_id, ','.join(user_ids)))
            conn.commit()

    def get_upcoming_events(self, user_id, group_id):
        ic("debug listing events", user_id, group_id)
        with self.get_db_connection() as conn:
            c = conn.cursor()
            if group_id is not None:
                c.execute('''
                    SELECT id, title, description, event_date, location, group_id, user_ids
                    FROM events
                    WHERE group_id = ? AND event_date >= datetime('now')
                    ORDER BY event_date ASC
                ''', (group_id,))
            else: 
                c.execute('''
                    SELECT id, title, description, event_date, location, group_id, user_ids
                    FROM events
                    WHERE user_ids = ? AND event_date >= datetime('now')
                    ORDER BY event_date ASC
                ''', (user_id,))
            return c.fetchall()

    def delete_event(self, event_id):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM events WHERE id = ?', (event_id,))
            conn.commit()
