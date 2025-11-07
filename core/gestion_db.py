import sqlite3
from datetime import datetime
import threading
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "identifier.sqlite")

_db_lock = threading.Lock()

# ==============================
# CONNEXION & UTILITAIRES
# ==============================
def get_connection():
    """Crée une connexion indépendante (thread-safe)"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def execute_write(query, params=()):
    with _db_lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()

def execute_fetchall(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# ==============================
# INITIALISATION DE LA BASE
# ==============================
def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        added_by INTEGER,
        added_at TEXT DEFAULT (datetime('now')),
        status TEXT DEFAULT 'active',
        FOREIGN KEY (added_by) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS baseline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_id INTEGER NOT NULL,
        path TEXT UNIQUE NOT NULL,
        hash TEXT,
        size INTEGER,
        modified_time TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(folder_id) REFERENCES folders(id)
    );

    CREATE TABLE IF NOT EXISTS suspects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baseline_id INTEGER,
    path TEXT UNIQUE NOT NULL,       
    old_hash TEXT,
    last_hash TEXT,
    state TEXT CHECK(state IN ('modified','deleted','new')),
    first_detected TEXT DEFAULT (datetime('now')),
    last_seen TEXT,
    resolved INTEGER DEFAULT 0,
    FOREIGN KEY (baseline_id) REFERENCES baseline(id)
    );


    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT (datetime('now')),
        event_type TEXT CHECK(event_type IN ('info','warning','error','alert','baseline')),
        file_path TEXT,
        description TEXT,
        level TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        sent_at TEXT DEFAULT (datetime('now')),
        status TEXT CHECK(status IN ('sent','pending','failed')),
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_files_path ON baseline(path);
    CREATE INDEX IF NOT EXISTS idx_suspects_state ON suspects(state);
    CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
    CREATE INDEX IF NOT EXISTS idx_baseline_folder ON baseline(folder_id);
    """)
    conn.commit()
    conn.close()

# ==============================
# INSERTS DE BASELINE ET FOLDERS
# ==============================
def insert_folder(path):
    """Ajoute un dossier à surveiller (ou ignore s’il existe déjà)"""
    execute_write("INSERT OR IGNORE INTO folders (path) VALUES (?)", (path,))


def insert_baseline_entry(folder_id, path, hash_val, size, modified_time, username=None):
    """Insert or replace baseline; store optional username (owner)."""
    execute_write("""
        INSERT OR REPLACE INTO baseline (folder_id, path, hash, size, modified_time, username)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (folder_id, path, hash_val, size, modified_time, username))

def get_baseline_owner(path):
    """Return the username (owner) for a given baseline path, or None if not set."""
    rows = execute_fetchall("SELECT username FROM baseline WHERE path=?", (path,))
    return rows[0][0] if rows and rows[0][0] is not None else None

def set_baseline_owner(path, username):
    """Set/transfer owner for a given baseline file (admin-only operation intended)."""
    execute_write("UPDATE baseline SET username=? WHERE path=?", (username, path))


def get_folder_id(path):
    """Retourne l’ID du dossier surveillé"""
    rows = execute_fetchall("SELECT id FROM folders WHERE path=?", (path,))
    return rows[0][0] if rows else None

def get_baseline():
    """Retourne {path: hash} de tous les fichiers surveillés"""
    rows = execute_fetchall("SELECT path, hash FROM baseline")
    return {path: hash_val for path, hash_val in rows}

# ==============================
# OPS SUR BASELINE ET FOLDERS
# ==============================
def insert_folder_and_baseline_for_path(folder):
    """Crée la baseline complète pour un dossier (appelée depuis build_baseline_for_folder)"""
    insert_folder(folder)
    folder_id = get_folder_id(folder)
    if not folder_id:
        return

    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                with open(full_path, "rb") as file:
                    h = hashlib.sha256(file.read()).hexdigest()
                st = os.stat(full_path)
                insert_baseline_entry(folder_id, full_path, h, st.st_size, datetime.fromtimestamp(st.st_mtime).isoformat())
                count += 1
            except Exception :
                continue

    log_event("info", f"{count} fichiers enregistrés pour {folder}")
    return count

# ==============================
# SUSPECTS HANDLING
# ==============================
def upsert_suspect(path, old_hash, last_hash, state):
    """Ajoute ou met à jour un fichier suspect"""
    execute_write("""
        INSERT INTO suspects (path, old_hash, last_hash, state, first_detected, last_seen)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(path) DO UPDATE SET
            last_hash=excluded.last_hash,
            last_seen=datetime('now'),
            state=excluded.state
    """, (path, old_hash, last_hash, state))

def remove_suspect(path):
    """Supprime un suspect résolu"""
    execute_write("DELETE FROM suspects WHERE path=?", (path,))



def get_suspects_map():
    """Retourne {path: last_hash} depuis la table suspects."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT path, last_hash FROM suspects")
    data = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()
    return data

def is_suspect(path):
    """Return True if a file is already flagged as suspect."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM suspects WHERE path=? AND resolved=0", (path,))
        return cur.fetchone() is not None


def get_all_suspects():
    """Retourne tous les fichiers suspects"""
    return execute_fetchall("SELECT path, state, last_seen FROM suspects WHERE resolved=0")

# ==============================
# EVENTS & NOTIFICATIONS
# ==============================
def log_event(event_type, description, level="info", file_path=None, user_id=None):
    """Logge un événement dans la table events"""
    # si event_type invalide => remplacer par "info" (évite IntegrityError)
    valid_types = ["info", "warning", "error", "alert", "baseline"]
    if event_type not in valid_types:
        event_type = "info"

    execute_write("""
        INSERT INTO events (event_type, description, level, file_path, user_id)
        VALUES (?, ?, ?, ?, ?)
    """, (event_type, description, level, file_path, user_id))

def add_notification(title, message, status="pending", user_id=None):
    """Ajoute une notification à la table"""
    execute_write("""
        INSERT INTO notifications (title, message, status, user_id)
        VALUES (?, ?, ?, ?)
    """, (title, message, status, user_id))

def mark_notification_sent(notification_id):
    """Marque une notification comme envoyée"""
    execute_write("UPDATE notifications SET status='sent', sent_at=datetime('now') WHERE id=?", (notification_id,))

# ==============================
# USERS (OPTIONNEL)
# ==============================
def add_user(username, password_hash, email, role="user"):
    """Ajoute un utilisateur"""
    execute_write("""
        INSERT OR IGNORE INTO users (username, password_hash, email, role)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, email, role))

def get_user_by_email(email):
    """Retourne les infos d’un utilisateur"""
    rows = execute_fetchall("SELECT id, username, email, role FROM users WHERE email=?", (email,))
    return rows[0] if rows else None

# ==============================
# HELPERS
# ==============================
def get_baseline_dict():
    """Alias pour compatibilité"""
    return get_baseline()



# ==============================
# DASHBOARD / STATISTICS
# ==============================

def get_dashboard_stats():
    """Return a summary of global stats for the dashboard."""
    stats = {}

    # Total folders and baseline files
    stats["total_folders"] = execute_fetchall("SELECT COUNT(*) FROM folders")[0][0]
    stats["total_baseline_files"] = execute_fetchall("SELECT COUNT(*) FROM baseline")[0][0]

    # Suspects by type
    stats["suspects_total"] = execute_fetchall("SELECT COUNT(*) FROM suspects WHERE resolved=0")[0][0]
    stats["suspects_modified"] = execute_fetchall("SELECT COUNT(*) FROM suspects WHERE state='modified' AND resolved=0")[0][0]
    stats["suspects_deleted"] = execute_fetchall("SELECT COUNT(*) FROM suspects WHERE state='deleted' AND resolved=0")[0][0]
    stats["suspects_new"] = execute_fetchall("SELECT COUNT(*) FROM suspects WHERE state='new' AND resolved=0")[0][0]

    # Events count by type
    stats["events_info"] = execute_fetchall("SELECT COUNT(*) FROM events WHERE event_type='info'")[0][0]
    stats["events_alert"] = execute_fetchall("SELECT COUNT(*) FROM events WHERE event_type='alert'")[0][0]
    stats["events_warning"] = execute_fetchall("SELECT COUNT(*) FROM events WHERE event_type='warning'")[0][0]
    stats["events_error"] = execute_fetchall("SELECT COUNT(*) FROM events WHERE event_type='error'")[0][0]

    # Pending notifications
    stats["pending_notifications"] = execute_fetchall("SELECT COUNT(*) FROM notifications WHERE status='pending'")[0][0]

    return stats


def get_recent_events(limit=10):
    """Return the N most recent events."""
    return execute_fetchall("""
        SELECT timestamp, event_type, description, file_path, level
        FROM events
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))


def get_suspect_trend(days=7):
    """Return count of new suspects per day (for the last N days)."""
    return execute_fetchall(f"""
        SELECT strftime('%Y-%m-%d', first_detected) AS day, COUNT(*)
        FROM suspects
        WHERE first_detected >= datetime('now', '-{days} days')
        GROUP BY day
        ORDER BY day 
    """)


def get_event_trend(days=7):
    """Return number of events per day (for charts)."""
    return execute_fetchall(f"""
        SELECT strftime('%Y-%m-%d', timestamp) AS day, COUNT(*)
        FROM events
        WHERE timestamp >= datetime('now', '-{days} days')
        GROUP BY day
        ORDER BY day 
    """)


def get_top_modified_files(limit=5):
    """Return top modified files (recent suspects)."""
    return execute_fetchall("""
        SELECT path, state, last_seen
        FROM suspects
        WHERE resolved=0 AND state='modified'
        ORDER BY last_seen DESC
        LIMIT ?
    """, (limit,))


def get_notifications(limit=5):
    """Return latest notifications."""
    return execute_fetchall("""
        SELECT title, message, status, sent_at
        FROM notifications
        ORDER BY sent_at DESC
        LIMIT ?
    """, (limit,))
