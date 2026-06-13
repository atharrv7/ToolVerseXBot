import sqlite3
from datetime import datetime
from ..config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    join_date TEXT,
                    commands_executed INTEGER DEFAULT 0,
                    qr_generated INTEGER DEFAULT 0,
                    passwords_generated INTEGER DEFAULT 0
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    feature_name TEXT PRIMARY KEY,
                    usage_count INTEGER DEFAULT 0
                )
            """)

    def add_user(self, user_id, username):
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)",
                (user_id, username, join_date)
            )

    def log_command(self, user_id, feature_name):
        with self.conn:
            # Update user stats
            self.conn.execute(
                "UPDATE users SET commands_executed = commands_executed + 1 WHERE user_id = ?",
                (user_id,)
            )
            if feature_name == "qr_generator":
                self.conn.execute("UPDATE users SET qr_generated = qr_generated + 1 WHERE user_id = ?", (user_id,))
            elif feature_name == "password_generator":
                self.conn.execute("UPDATE users SET passwords_generated = passwords_generated + 1 WHERE user_id = ?", (user_id,))
            
            # Update global feature stats
            self.conn.execute(
                "INSERT INTO stats (feature_name, usage_count) VALUES (?, 1) "
                "ON CONFLICT(feature_name) DO UPDATE SET usage_count = usage_count + 1",
                (feature_name,)
            )

    def get_user_stats(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

    def get_global_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT feature_name, usage_count FROM stats ORDER BY usage_count DESC LIMIT 1")
        most_used = cursor.fetchone()
        
        cursor.execute("SELECT SUM(usage_count) FROM stats")
        total_commands = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(qr_generated) FROM users")
        total_qr = cursor.fetchone()[0] or 0
        
        return {
            "total_users": total_users,
            "most_used_feature": most_used[0] if most_used else "None",
            "total_commands": total_commands,
            "qr_generation_count": total_qr
        }

db = DatabaseManager()
