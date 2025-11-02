import hashlib
import os
import time
from plyer import notification
from core.gestion_db import *
from datetime import datetime
import threading

CHECK_INTERVAL = 10  # secondes
running = False
_db_lock = threading.Lock()
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "log.txt")

def get_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def notify_user(title, msg):
    try:
        notification.notify(title=title, message=msg, timeout=5)
    except:
        pass

def log_to_file(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")


def build_baseline_for_folder(folder):
    """Analyse un dossier et enregistre son état dans la base SQLite."""
    insert_folder(folder)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM folders WHERE path=?", (folder,))
    folder_id = c.fetchone()[0]
    conn.close()

    count = 0
    for root, _, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            h = get_file_hash(path)
            if h:
                st = os.stat(path)
                insert_baseline_entry(
                    folder_id,
                    path,
                    h,
                    st.st_size,
                    datetime.fromtimestamp(st.st_mtime).isoformat()
                )
                count += 1

    notify_user("Baseline créée", f"{count} fichiers ajoutés depuis {folder}")
    log_event("baseline", f"Baseline créée pour {folder} ({count} fichiers)")
    log_to_file(f"Baseline créée pour {folder} ({count} fichiers)")


# ==============================
# INTÉGRITÉ
# ==============================
def check_integrity():
    baseline_map = get_baseline()
    ok_count = mod_count = del_count = 0
    file_status = []

    for path, expected_hash in baseline_map.items():
        current_hash = get_file_hash(path)

        if current_hash is None:
            upsert_suspect(path, expected_hash, None, "deleted")
            del_count += 1
            file_status.append((path, "❌ Supprimé"))

        elif current_hash != expected_hash:
            upsert_suspect(path, expected_hash, current_hash, "modified")
            mod_count += 1
            file_status.append((path, "⚠️ Modifié"))

        else:
            remove_suspect(path)
            ok_count += 1
            file_status.append((path, "✅ OK"))

    log_event("info", f"OK={ok_count}, Modifiés={mod_count}, Supprimés={del_count}")
    return ok_count, mod_count, del_count, file_status


# ==============================
# THREAD DE SURVEILLANCE
# ==============================

def _monitor_loop():
    global running
    while running:
        try:
            ok, mod, sup, _ = check_integrity()
            if mod > 0 or sup > 0:
                notify_user("Alerte FIM", f"{mod} modifiés, {sup} supprimés détectés.")
                log_to_file(f"[ALERTE] {mod} modifiés, {sup} supprimés")
        except Exception as e:
            log_to_file(f"Erreur dans monitor_loop: {e}")
        time.sleep(CHECK_INTERVAL)

def start_monitoring():
    global running, _monitor_thread
    if running:
        return None
    running = True
    _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
    _monitor_thread.start()
    return _monitor_thread

def stop_monitoring():
    global running
    running = False