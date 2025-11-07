import os
import hashlib
import time
import shutil
from datetime import datetime
from plyer import notification
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import gestion_db as db  # ✅ use your DB module
BACKUP_DIR = "data/backups"

ACL = {
    "admin": ["read", "modify", "delete", "create"],
    "user": ["read"],
    "guest": ["read"]
}

current_user = ""
current_user_id = None  # linked to DB user

# ===============================
# 🔹 UTILITIES
# ===============================
def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_file(path):
    ensure_backup_dir()
    if os.path.exists(path):
        backup_path = os.path.join(BACKUP_DIR, os.path.basename(path))
        shutil.copy2(path, backup_path)
        db.log_event("info", f"Sauvegarde créée : {backup_path}", user_id=current_user_id)
        print(f"💾 Backup created: {backup_path}")

def restore_file(filename):
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(filename))
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filename)
        db.log_event("alert", f"Fichier restauré : {filename}", user_id=current_user_id)
        notify("Fichier restauré", os.path.basename(filename))
    else:
        db.log_event("warning", f"Aucune sauvegarde trouvée pour {filename}", user_id=current_user_id)

def delete_file(path):
    try:
        os.remove(path)
        db.log_event("alert", f"Fichier supprimé automatiquement : {path}", user_id=current_user_id)
        notify("Création non autorisée", os.path.basename(path))
    except Exception as e:
        db.log_event("error", f"Erreur suppression {path}: {e}", user_id=current_user_id)

def notify(title, message):
    try:
        notification.notify(title=title, message=message, timeout=4)
        db.add_notification(title, message, user_id=current_user_id)
    except Exception:
        pass

def get_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

# ===============================
# 🔐 ACL CHECK
# ===============================

def is_authorized(action, filepath=None):
    """
    Returns True if current_user is allowed to perform `action` on filepath.
    Rules:
    - Admin bypasses everything.
    - If user's role (ACL) grants the action, allow.
    - If file has an owner:
        - allow if owner == current_user OR current_user == 'admin'
        - otherwise deny (unless role permits global modify)
    - If file owner is None: allow based on role (ACL).
    """
    # admin override
    if current_user == "admin":
        return True

    # basic role check
    role_perms = ACL.get(current_user, []) or ACL.get("guest", [])
    if action in role_perms:
        # allowed by role globally (e.g., users with modify right)
        return True

    # if filepath is specified, check owner
    if filepath:
        owner = db.get_baseline_owner(filepath)
        # owner not set => decide by role (already checked above)
        if owner is None:
            return action in role_perms
        # owner set: allow only owner or admin (admin handled above)
        if owner == current_user:
            return True
        # otherwise deny
        db.log_event("warning", f"Accès refusé pour {current_user} sur {filepath}")
        notify("Accès bloqué", os.path.basename(filepath))
        return False

    # fallback deny
    return False

# ===============================
# 📁 BASELINE CREATION
# ===============================
def build_baseline_for_folder(folder, current_user):
    # when building baseline for a folder, store no owner so other users can modify later
    db.insert_folder(folder)
    folder_id = db.get_folder_id(folder)
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
                # <-- store username = None for shared baseline
                db.insert_baseline_entry(folder_id, full_path, h, st.st_size, datetime.fromtimestamp(st.st_mtime).isoformat(), username=current_user)
                count += 1
            except Exception:
                continue

    db.log_event("info", f"{count} fichiers enregistrés pour {folder}")
    notify("Baseline mise à jour", f"Fichiers ajoutés pour {folder}")
    return count

# ===============================
# 👁️ FILE SYSTEM MONITOR
# ===============================
class IntegrityHandler(FileSystemEventHandler):
    def __init__(self, folder):
        self.folder = folder
        self.baseline = db.get_baseline_dict()

    def on_created(self, event):
        if event.is_directory:
            return
        path = event.src_path
        h = get_file_hash(path)

        if path not in self.baseline:
            if not is_authorized("create", path):
                db.log_event("alert", f"Création non autorisée par {current_user}: {path}")
                delete_file(path)
            else:
                folder_id = db.get_folder_id(self.folder)
                st = os.stat(path)
                db.insert_baseline_entry(folder_id, path, h, st.st_size, datetime.fromtimestamp(st.st_mtime).isoformat(), username=current_user)

                backup_file(path)
                db.log_event("baseline", f"Nouveau fichier ajouté : {path}")
                notify("Fichier ajouté", os.path.basename(path))

    def on_modified(self, event):
        if event.is_directory:
            return
        path = event.src_path
        h = get_file_hash(path)
        if not h:
            return

        baseline_map = db.get_baseline_dict()
        old_hash = baseline_map.get(path)

        if old_hash and h != old_hash:
            db.upsert_suspect(path, old_hash, h, "modified")
            if not is_authorized("modify", path):
                db.log_event("alert", f"Modification non autorisée : {path}")
                restore_file(path)
            else:
                backup_file(path)
                folder_id = db.get_folder_id(self.folder)
                st = os.stat(path)
                owner = db.get_baseline_owner(path)
                db.insert_baseline_entry(folder_id, path, h, st.st_size,
                                         datetime.fromtimestamp(st.st_mtime).isoformat(), username=owner)

                db.log_event("info", f"Fichier modifié et baseline mise à jour : {path}")
                notify("Fichier modifié", os.path.basename(path))

    def on_deleted(self, event):
        if event.is_directory:
            return
        path = event.src_path
        db.upsert_suspect(path, None, None, "deleted")
        if not is_authorized("delete", path):
            db.log_event("alert", f"Suppression non autorisée : restauration {path}")
            restore_file(path)
            print(path)
        else:
            db.log_event("info", f"Suppression autorisée : {path}")

# ===============================
# 🚀 MONITOR START
# ===============================




import os
import time
import threading


# === If your FIM file is named differently, adjust the import above ===
from integrity_monitoring import start_monitoring, build_baseline_for_folder

def select_folder():
    """Ask user to enter folder path (or use default)"""
    folder = input("\n📂 Enter folder path to monitor (or press Enter for default): ").strip()
    if not folder:
        folder = r"C:\Users\DELL\Desktop\test"
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"✅ Folder created: {folder}")
    return folder


def start_fim(folder, username):
    """Start monitoring thread"""

    globals()['current_user'] = username
    globals()['current_user_id'] = db.get_user_id(username) if hasattr(db, "get_user_id") else None

    print(f"\n🔒 Monitoring started by '{username}' on: {folder}")
    build_baseline_for_folder(folder)

    # Run in separate thread so you can stop it
    thread = threading.Thread(target=start_monitoring, args=(folder,), daemon=True)
    thread.start()

    print("🕵️ Press Ctrl+C to stop monitoring.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")


def main():
    print("=== File Integrity Monitoring ===")
    db.init_db()

    username = input("👤 Enter username (admin/user/guest): ").strip().lower()
    if username not in ["admin", "user", "guest"]:
        print("❌ Invalid username.")
        return

    folder = select_folder()

    print(f"\n👋 Welcome, {username}!")
    print(f"Folder to monitor: {folder}")
    print("\nStarting baseline and file watcher...")

    start_fim(folder, username)


if __name__ == "__main__":
    main()

