import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

class DatabaseConstants:
    REMINDER_INTERVAL = 60       # seconds
    MAX_ACTIVITY_LOGS = 100
    MAX_TITLE_LENGTH = 100
    TIME_FORMAT = "%H:%M"
    DATE_FORMAT = "%Y-%m-%d"
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

class Database:
    def __init__(self, db_path: str):
        Path("data").mkdir(exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    time TEXT NOT NULL,
                    recurring INTEGER DEFAULT 0,
                    last_fired_date TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    photo_path TEXT,
                    audio_path TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    number TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS medical_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        try:
            with self.conn:
                return self.conn.execute(query, params)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()

    # --- Reminders ---
    def add_reminder(self, title: str, time_str: str, recurring: bool) -> None:
        self.execute(
            "INSERT INTO reminders (title, time, recurring) VALUES (?,?,?)",
            (title, time_str, int(bool(recurring)))
        )
        self.add_activity(f"Reminder added: {title} at {time_str}")

    def get_reminders(self) -> List[Tuple]:
        return self.execute("SELECT id, title, time, recurring FROM reminders").fetchall()

    def delete_reminder(self, rid: int) -> None:
        self.execute("DELETE FROM reminders WHERE id=?", (rid,))
        self.add_activity(f"Reminder deleted ID: {rid}")

    # --- Faces ---
    def add_face(self, name: str, relation: str, photo: str, audio: Optional[str] = None) -> None:
        self.execute(
            "INSERT INTO faces (name, relation, photo_path, audio_path) VALUES (?,?,?,?)",
            (name, relation, photo, audio)
        )
        self.add_activity(f"Face added: {name} ({relation})")

    def get_faces(self) -> List[Tuple]:
        return self.execute("SELECT id, name, relation, photo_path, audio_path FROM faces").fetchall()

    def delete_face(self, fid: int) -> None:
        self.execute("DELETE FROM faces WHERE id=?", (fid,))
        self.add_activity(f"Face deleted ID: {fid}")

    # --- Contacts ---
    def add_contact(self, name: str, number: str) -> None:
        self.execute("INSERT INTO contacts (name, number) VALUES (?,?)", (name, number))
        self.add_activity(f"Contact added: {name}")

    def get_contacts(self) -> List[Tuple]:
        return self.execute("SELECT id, name, number FROM contacts").fetchall()

    def delete_contact(self, cid: int) -> None:
        self.execute("DELETE FROM contacts WHERE id=?", (cid,))
        self.add_activity(f"Contact deleted ID: {cid}")

    # --- Activity Log ---
    def add_activity(self, msg: str) -> None:
        ts = datetime.now().isoformat()  # Local time, NOT utcnow()
        self.execute("INSERT INTO activity (ts, message) VALUES (?,?)", (ts, msg))
        # Optional: Truncate old logs
        self.execute(f"""
            DELETE FROM activity WHERE id NOT IN (
                SELECT id FROM activity ORDER BY id DESC LIMIT {DatabaseConstants.MAX_ACTIVITY_LOGS}
            )
        """)

    def get_activities(self) -> List[Tuple]:
        return self.execute("SELECT ts, message FROM activity ORDER BY id DESC").fetchall()

    # --- Medical Records ---
    def add_record(self, title: str, details: str) -> None:
        self.execute("INSERT INTO medical_records (title, details) VALUES (?,?)", (title, details))
        self.add_activity(f"Medical record added: {title}")

    def get_records(self) -> List[Tuple]:
        return self.execute("SELECT id, title, details FROM medical_records").fetchall()

    def delete_record(self, rid: int) -> None:
        self.execute("DELETE FROM medical_records WHERE id=?", (rid,))
        self.add_activity(f"Medical record deleted ID: {rid}")
