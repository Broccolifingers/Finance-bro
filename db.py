"""
Finance Bro — Database Layer
-----------------------------
All SQLite schema definitions and CRUD helper functions live here.
Uses a single local file `finance_bro.db` so the app is 100% offline-capable.
"""

import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance_bro.db")


def get_connection():
    """Return a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            monthly_income REAL DEFAULT 0,
            current_balance REAL DEFAULT 0,
            goal_name TEXT,
            goal_amount REAL DEFAULT 0,
            goal_saved REAL DEFAULT 0,
            personality TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            motivation TEXT,
            worth_it_score REAL,
            verdict TEXT,
            decision TEXT,          -- 'bought' or 'skipped'
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS personality_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            personality_type TEXT,
            score_json TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            streak_type TEXT NOT NULL,   -- 'no_impulse', 'budget', 'saving'
            current_count INTEGER DEFAULT 0,
            best_count INTEGER DEFAULT 0,
            last_updated TEXT,
            UNIQUE(user_id, streak_type),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_name TEXT NOT NULL,
            earned_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,   -- 'user' or 'bro'
            message TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()
    conn.close()


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------- USERS ----

def create_user(name, age, monthly_income, current_balance, goal_name, goal_amount, goal_saved=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO users (name, age, monthly_income, current_balance,
                               goal_name, goal_amount, goal_saved, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, age, monthly_income, current_balance, goal_name, goal_amount, goal_saved, now()),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_latest_user():
    """Convenience: for a single-user local app, grab the most recently created profile."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_field(user_id, field, value):
    allowed = {
        "name", "age", "monthly_income", "current_balance",
        "goal_name", "goal_amount", "goal_saved", "personality",
    }
    if field not in allowed:
        raise ValueError(f"Field '{field}' is not editable.")
    conn = get_connection()
    conn.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (value, user_id))
    conn.commit()
    conn.close()


def adjust_balance(user_id, delta):
    conn = get_connection()
    conn.execute("UPDATE users SET current_balance = current_balance + ? WHERE id = ?", (delta, user_id))
    conn.commit()
    conn.close()


def adjust_goal_saved(user_id, delta):
    conn = get_connection()
    conn.execute("UPDATE users SET goal_saved = goal_saved + ? WHERE id = ?", (delta, user_id))
    conn.commit()
    conn.close()


# ------------------------------------------------------------ PURCHASES ----

def add_purchase(user_id, product_name, price, category, motivation, worth_it_score, verdict, decision):
    conn = get_connection()
    conn.execute(
        """INSERT INTO purchases (user_id, product_name, price, category, motivation,
                                   worth_it_score, verdict, decision, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, product_name, price, category, motivation, worth_it_score, verdict, decision, now()),
    )
    conn.commit()
    conn.close()


def get_purchases(user_id, limit=None):
    conn = get_connection()
    q = "SELECT * FROM purchases WHERE user_id = ? ORDER BY created_at DESC"
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = conn.execute(q, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --------------------------------------------------------- PERSONALITY ----

def save_personality_result(user_id, personality_type, score_json):
    conn = get_connection()
    conn.execute(
        "INSERT INTO personality_results (user_id, personality_type, score_json, created_at) VALUES (?, ?, ?, ?)",
        (user_id, personality_type, score_json, now()),
    )
    conn.commit()
    conn.close()
    update_user_field(user_id, "personality", personality_type)


# -------------------------------------------------------------- STREAKS ----

def get_streak(user_id, streak_type):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM streaks WHERE user_id = ? AND streak_type = ?", (user_id, streak_type)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def bump_streak(user_id, streak_type, reset=False):
    """Increment (or reset) a streak counter and return the new value."""
    existing = get_streak(user_id, streak_type)
    conn = get_connection()
    if existing is None:
        new_count = 0 if reset else 1
        conn.execute(
            "INSERT INTO streaks (user_id, streak_type, current_count, best_count, last_updated) VALUES (?, ?, ?, ?, ?)",
            (user_id, streak_type, new_count, new_count, now()),
        )
    else:
        new_count = 0 if reset else existing["current_count"] + 1
        best = max(new_count, existing["best_count"])
        conn.execute(
            "UPDATE streaks SET current_count = ?, best_count = ?, last_updated = ? WHERE user_id = ? AND streak_type = ?",
            (new_count, best, now(), user_id, streak_type),
        )
    conn.commit()
    conn.close()
    return new_count


def get_all_streaks(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM streaks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --------------------------------------------------------------- BADGES ----

def award_badge(user_id, badge_name):
    conn = get_connection()
    existing = conn.execute(
        "SELECT 1 FROM badges WHERE user_id = ? AND badge_name = ?", (user_id, badge_name)
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO badges (user_id, badge_name, earned_at) VALUES (?, ?, ?)",
            (user_id, badge_name, now()),
        )
        conn.commit()
    conn.close()
    return existing is None  # True if newly awarded


def get_badges(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM badges WHERE user_id = ? ORDER BY earned_at", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ------------------------------------------------------------- CHAT LOG ----

def log_chat(user_id, role, message):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_log (user_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (user_id, role, message, now()),
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM chat_log WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows][::-1]


def seed_dummy_data(user_id):
    """Populate a few sample purchases/streaks so the dashboard looks alive on first run."""
    sample_purchases = [
        ("AirPods Pro", 24900, "Tech", "Trend", 6.5, "Think Carefully", "bought"),
        ("Coffee Subscription", 999, "Food", "Reward", 8.0, "Worth It", "bought"),
        ("Limited Sneakers", 8999, "Fashion", "Social Pressure", 3.2, "Bad Financial Decision", "skipped"),
        ("Online Course", 1499, "Education", "Need", 9.1, "Worth It", "bought"),
    ]
    for p in sample_purchases:
        add_purchase(user_id, *p)
    bump_streak(user_id, "no_impulse")
    bump_streak(user_id, "no_impulse")
    bump_streak(user_id, "budget")
    award_badge(user_id, "Bronze Bro")
