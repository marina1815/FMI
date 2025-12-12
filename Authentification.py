from PyQt6.QtGui import QFont, QPixmap , QIcon
from PyQt6.QtWidgets import *
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from core.user_manager import (
    load_current_user, get_email_by_username, get_hashed_password_by_username,
    get_date_of_birth_by_username, edit_user, hash_password, list_users,verify_login
)
import  os

basee_dir = os.path.dirname(os.path.abspath(__file__))

icon_path_light = os.path.join(basee_dir, "img/iconFortiFile.PNG")


import os
import threading
import hashlib
import time
import shutil
from datetime import datetime
from plyer import notification
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import core.gestion_db as db
from core.gestion_db import *
from core.gestion_db import update_baseline_path, get_files

from core.user_manager import load_current_user
import json

# ===============================
# 🔹 VARIABLES GLOBALES
# ===============================
OBSERVERS = {}
BACKUP_DIR = "data/backups"
RESTORED_JSON = os.path.join("data", "restored_files.json")
current_user = ""
_db_lock = threading.Lock()


# ===============================
# 🔹 UTILITAIRES
# ===============================
def normalize_path(path):
    """Normalise le chemin pour Windows/Unix (slash et casse)."""
    return os.path.normcase(os.path.abspath(path))


def get_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None





def notify(title, message):
    try:
        notification.notify(title=title, message=message, timeout=4)
        db.add_notification(title, message, username=current_user)
    except Exception:
        pass


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_file(path):
    ensure_backup_dir()
    if os.path.exists(path):
        backup_path = os.path.join(BACKUP_DIR, os.path.basename(path))

        shutil.copy2(path, backup_path)
        db.log_event("info", f"Sauvegarde créée : {backup_path}", username=current_user)
        print(f"💾 Backup created: {backup_path}")


def delete_backup_file(path):
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(path))
    backup_path = os.path.normpath(backup_path).replace("\\", "/")

    if os.path.exists(backup_path):
        try:
            os.remove(backup_path)
            db.log_event("info", f"Backup supprimé : {backup_path}", username=current_user)
        except Exception as e:
            db.log_event("error", f"Erreur suppression backup {backup_path}: {e}", username=current_user)


def restore_file(filename, user):
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(filename))

    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filename)
        db.log_event("alert", f"Fichier restauré : {filename}", username=user)
        notify("Fichier restaure", f"{filename}")

    else:
        db.log_event("warning", f"Aucune sauvegarde trouvée pour {filename}", username=user)


def insert_files_restored(path, owner):
    """
    Ajoute une entrée dans restored_files.json pour tracer les restaurations.
    - path : chemin du fichier restauré
    - owner : utilisateur propriétaire du fichier (get_baseline_owner)
    """
    try:
        os.makedirs(os.path.dirname(RESTORED_JSON), exist_ok=True)

        # Charger les données existantes si le fichier existe
        if os.path.exists(RESTORED_JSON):
            with open(RESTORED_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        # Ajouter la nouvelle entrée
        entry = {
            "path": path,
            "owner": owner,
        }
        if not any(e["path"] == entry["path"] and e["owner"] == entry["owner"] for e in data):
            data.append(entry)

        # Sauvegarder dans le fichier JSON
        with open(RESTORED_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"📄 Fichier restauré enregistré dans {RESTORED_JSON}: {entry}")

    except Exception as e:
        print(f"[ERROR] Impossible d'écrire dans {RESTORED_JSON}: {e}")


def delete_file(path):
    try:
        os.remove(path)
        db.log_event("alert", f"Fichier supprimé automatiquement : {path}", username=current_user)
        notify("Création non autorisée", os.path.basename(path))
    except Exception as e:
        db.log_event("error", f"Erreur suppression {path}: {e}", username=current_user)


# ===============================
# 🔹 AUTORISATION
# ===============================
def is_authorized(filepath=None):
    global current_user
    if current_user == "admin":
        return True
    elif current_user in ["user", "guest"]:
        return False

    if filepath:

        owner = db.get_baseline_owner(filepath)
        if owner and "," in owner:
            owner_list = owner.split(",")

        else:
            owner_list = [owner] if owner else []

        if owner and current_user in owner_list:
            return True
        db.log_event("warning", f"Accès refusé : {current_user} sur {filepath}", username=current_user)
    return False


def normalize_path(path):
    """Normalise le chemin pour Windows/Unix (slash et casse)."""
    return os.path.normcase(os.path.abspath(path))


def get_baseline_hash(path):
    """
    Retourne le hash de baseline pour un fichier donné.
    - path : chemin du fichier
    - renvoie le hash SHA-256 enregistré ou None si non trouvé
    """
    # Récupère la baseline depuis la DB
    baseline_map = db.get_baseline_dict()

    if not baseline_map:
        return None

    # Normalise tous les chemins pour correspondre au format de event.src_path
    baseline_map = {normalize_path(p): h for p, h in baseline_map.items()}

    # Normalise le chemin demandé
    path = normalize_path(path)

    # Renvoie le hash si présent
    return baseline_map.get(path)


# ===============================
# 🔹 INTEGRITY HANDLER (Watchdog)
# ===============================
class IntegrityHandler(FileSystemEventHandler):

    def __init__(self, monitored_files, currentuser):
        self.monitored_files = [normalize_path(f) for f in monitored_files]
        self.baseline = db.get_baseline_dict()
        self.current_user = current_user

        print("init handler")

    def on_any_event(self, event):
        """Ignore les dossiers, ne traite que les fichiers surveillés."""
        if event.is_directory:
            return
        path = normalize_path(event.src_path)
        if path not in self.monitored_files:
            return  # on ignore les fichiers non surveillés

    def on_created(self, event):
        if event.is_directory:
            return
        path = normalize_path(event.src_path)
        if path not in self.monitored_files:
            return
        print(f"[CREATE] {path}")
        notify("Fichier ajouté", os.path.basename(path))
        """
        if not is_authorized(path):
            db.log_event("alert", f"Création non autorisée : {path}", username=current_user)
            delete_file(path)
        else:
            h = get_file_hash(path)
            st = os.stat(path)
            db.insert_baseline_entry(None, path, h, st.st_size, datetime.fromtimestamp(st.st_mtime).isoformat(), username=current_user)
            backup_file(path)
            """

    def on_modified(self, event):
        if event.is_directory:
            return
        path = normalize_path(event.src_path)
        if path not in self.monitored_files:
            return
        print(f"[MODIFY] {path}")

        h = get_file_hash(path)
        old_hash = get_baseline_hash(path)
        if old_hash and h != old_hash:
            print(is_authorized(event.src_path), "is_authorized")
            if not is_authorized(event.src_path):

                db.log_event("alert", f"Modification non autorisée : {path}", username=self.current_user)
                notify("Modification bloquée", os.path.basename(path))
                print(path, "hiba")
                insert_files_restored(event.src_path, get_baseline_owner(event.src_path))
                print("hhhh")
            else:
                db.update_baseline(event.src_path, h)
                backup_file(path)
                owner = db.get_baseline_owner(event.src_path)
                if owner:
                    first_owner = owner.split(",")[0].strip()  # garde le premier et enlève les espaces
                else:
                    first_owner = None

                # Appel de upsert_suspect avec le premier utilisateur seulement
                if first_owner:
                    db.upsert_suspect(event.src_path, old_hash, h, "modified", first_owner)
                db.log_event("info", f"Fichier modifié : {path}", username=self.current_user)
                notify("Fichier modifié", os.path.basename(path))

    def on_deleted(self, event):
        if event.is_directory:
            return
        path = normalize_path(event.src_path)
        if path not in self.monitored_files:
            return
        print(f"[DELETE] {path}")

        if not is_authorized(event.src_path):
            db.log_event("alert", f"Suppression non autorisée : restauration {path}", username=self.current_user)
            notify("Suppression bloquée", os.path.basename(path))
            insert_files_restored(event.src_path, get_baseline_owner(event.src_path))

        else:

            h = get_file_hash(path)
            old_hash = get_baseline_hash(path)
            db.log_event("info", f"Suppression autorisée : {path}", username=self.current_user)
            notify("Suppression autorisée", os.path.basename(path))
            owner = db.get_baseline_owner(event.src_path)
            if owner:
                first_owner = owner.split(",")[0].strip()  # garde le premier et enlève les espaces
            else:
                first_owner = None

            # Appel de upsert_suspect avec le premier utilisateur seulement
            if first_owner:
                db.upsert_suspect(event.src_path, old_hash, h, "deleted", first_owner)
            db.delete_baseline_file(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        src = normalize_path(event.src_path)
        dest = normalize_path(event.dest_path)
        print(src)
        print(dest)
        print(event.src_path)
        print(event.dest_path)
        if src not in self.monitored_files:
            return
        db.log_event("info", f"Renommage : {src} -> {dest}", username=self.current_user)
        notify("Renommage de fichier", os.path.basename(dest))
        update_baseline_path(event.src_path, event.dest_path)




# ===============================
# 🔹 DEMARRER / ARRETER LA SURVEILLANCE
# ===============================
def _start_watcher_thread(file_list, username):
    global OBSERVERS
    handler = IntegrityHandler(file_list, username)
    observer = Observer()
    # On observe le dossier parent commun à tous les fichiers
    common_root = os.path.commonpath(file_list)
    observer.schedule(handler, common_root, recursive=True)
    observer.daemon = True
    observer.start()
    OBSERVERS[normalize_path(common_root)] = observer



def boucle_restore(user_current):
    """
    Restaure tous les fichiers associés à l'utilisateur admin (ou autre)
    puis les supprime du fichier restored_files.json.
    """
    try:
        if not os.path.exists(RESTORED_JSON):
            print("⚠️ Aucun fichier restored_files.json trouvé.")
            return

        # Charger les données existantes
        with open(RESTORED_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print("📂 Aucun fichier à restaurer.")
            return

        # Liste pour garder les entrées non traitées
        remaining = []

        for entry in data:
            path = entry.get("path")
            owner = entry.get("owner")
            owner_list = owner.split(",")

            # Si le fichier appartient à l'utilisateur courant → on le restaure
            if user_current in owner_list:
                print(f"♻️ Restauration du fichier : {path}")
                try:
                    restore_file(path, owner)
                    print(f"✅ Fichier restauré : {path}")
                except Exception as e:
                    print(f"❌ Erreur lors de la restauration de {path}: {e}")
                    remaining.append(entry)  # on le garde s’il a échoué
            else:
                remaining.append(entry)

        # Réécriture du fichier JSON sans les fichiers restaurés avec succès
        with open(RESTORED_JSON, "w", encoding="utf-8") as f:
            json.dump(remaining, f, indent=4, ensure_ascii=False)

        print(f"📦 Restauration terminée. {len(remaining)} entrées restantes dans {RESTORED_JSON}.")

    except Exception as e:
        print(f"[ERROR] boucle_restore: {e}")


def startMonitoring(file_list, username):
    global current_user

    current_user = username
    boucle_restore(current_user)
    th = threading.Thread(target=_start_watcher_thread, args=(file_list, username), daemon=True)
    th.start()
    print(f" Surveillance démarrée pour {len(file_list)} fichiers par '{username}'.")
    notify("Surveillance démarrée",f" par {username}")
    try:
        while True:  # boucle pour garder le programme actif
            time.sleep(1)
    except KeyboardInterrupt:
        stopMonitoring()


def stopMonitoring():
    global OBSERVERS
    for k, obs in list(OBSERVERS.items()):
        try:
            obs.stop()
            obs.join()

        except Exception:
            pass
    OBSERVERS.clear()
    print("🛑 Surveillance arrêtée.")

# Exemple :
   # Démarrer

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.login_button = None
        self.setWindowIcon(QIcon(icon_path_light))
        self.initUI()
        self.apply_theme()

    def initUI(self):
        # Configuration de la fenêtre
        self.setWindowTitle('Authentification')
        self.setFixedSize(400, 300)

        # Création d'un layout horizontal pour le titre et le logo
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)  # Réduire les marges
        title_layout.setSpacing(5)  # Réduire l'espace entre les éléments

        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap(icon_path_light).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setFixedSize(80, 80)

        # Titre
        self.title = QLabel("FortiFile-Authentification")
        self.title.setObjectName("titleLabel")
        #self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        #self.title.setStyleSheet("color: Black; margin: 0; padding: 0;")

        # Ajout du logo et du titre au layout horizontal
        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(self.title)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrer le tout

        # Username

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFixedHeight(35)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())


        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setFixedHeight(35)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.check_credentials)
        # Bouton de connexion - création d'un layout horizontal pour le centrer
        button_layout = QHBoxLayout()
        self.login_button = QPushButton(" Login ")
        self.login_button.setFixedHeight(35)
        self.login_button.setFixedWidth(200)  # Largeur fixe pour un meilleur aspect
        self.login_button.clicked.connect(self.check_credentials)
        

        # Ajouter le bouton au layout horizontal avec des stretches pour le centrer
        button_layout.addStretch(1)
        button_layout.addWidget(self.login_button)
        button_layout.addStretch(1)

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Marges internes
        layout.addLayout(title_layout)
        layout.addSpacing(20)
        layout.addWidget(self.username_input)
        layout.addSpacing(10)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addLayout(button_layout)  # Ajouter le layout du bouton centré
        layout.addStretch(1)  # Ajouter un stretch pour pousser tout vers le haut

        self.setLayout(layout)

    def apply_theme(self):
        """Thème clair/sombre"""
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 30px;
            }
            QLineEdit {
                background-color: #D6D9F5;
                color: black;
                border: 1px solid #151B54;
                border-radius: 6px;
                padding-left: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3342CC;
            }
            QPushButton {
                background-color: #151B54;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3342CC;
            }
               QLabel#titleLabel {
                color: Black;
                font-size: 18px;
                font-weight: bold;
                margin: 0;
                padding: 0;
            }
            QLabel {
                color: #151B54;
                font-weight: bold;
                font-size: 15px;
            }
        """)

    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()


        email = get_email_by_username(username)

        if email:
            # Utiliser la fonction verify_login avec l'email
            success, message = verify_login(email, password)
            if success:
                self.close()
                paths = get_files()
                startMonitoring(paths, username)

            else:
                QMessageBox.warning(self, 'Erreur', message)
        else:
            QMessageBox.warning(self, 'Erreur', 'Nom d\'utilisateur non trouvé')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())