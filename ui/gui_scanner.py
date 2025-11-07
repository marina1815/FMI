import os
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPainter, QColor
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QDateTime, pyqtProperty
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.config_manager import get_mode
from core.integrity_monitoring import *


class ShadowFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

    def apply_shadow_style(self):
        self.setStyleSheet("""
            ShadowFrame {
                background-color: white;
                border: 1px solid #3342CC;
                border-radius: 20px;
                margin: 5px;
            }
            ShadowFrame QLabel {
                color: black;
                font-weight: bold;
                background-color: white;
            }
            ShadowFrame QPushButton {
                color: black;
                background-color: #E0E0E0;
                border-radius: 10px;
                padding: 5px;
            }
            ShadowFrame:hover {
                border: 2px solid #3342CC;
            }
        """)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setColor(QColor("#1325d1"))
        shadow_effect.setOffset(0, 0)
        self.setGraphicsEffect(shadow_effect)

"""

 
btn add folder 
btn add file 
box  list file 
button start scan 
"""

class ScanPage(QWidget):
    def __init__(self, is_dark_theme=False, username=None, email=None):
        super().__init__()
        self.is_dark_theme = is_dark_theme
        self.username = username
        self.email = email

        self.apply_window_style()
        self.create_main_layout()
        self.create_main_content()



    # -------------------------
    # Fenêtre principale
    # -------------------------
    def create_main_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

    def apply_window_style(self):
        self.setStyleSheet("""
            QWidget {
                margin:0px;
                padding:0px;
                background-color: #e1e1e3;
            }
            QPushButton{
            background-color: #2301C0;
            color: white; border-radius: 8px;
            padding: 12px; font-size: 15px; font-weight: bold;
        }
        QPushButton :hover {
                background-color: #120A37;
            }
        """)

    # -------------------------
    # Content principal
    # -------------------------
    def create_main_content(self):
        self.main_content = QWidget()
        self.main_layout.addWidget(self.main_content)
        self.main_content_layout = QVBoxLayout(self.main_content)
        self.main_content_layout.setContentsMargins(10, 10, 10, 10)
        self.main_content_layout.setSpacing(20)

        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch()
        self.main_content_layout.addWidget(header_widget)

        # Section icône + texte
        icon_text_widget = QWidget()
        icon_text_layout = QHBoxLayout(icon_text_widget)
        icon_text_layout.setSpacing(20)
        icon_text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Sections gauche/droite
        self.sections_widget = QWidget()
        self.sections_layout = QHBoxLayout(self.sections_widget)
        self.sections_layout.setSpacing(20)
        self.main_content_layout.addWidget(self.sections_widget)

        # Colonne gauche
        self.left_column = QWidget()
        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setSpacing(20)
        self.sections_layout.addWidget(self.left_column, stretch=2)

        # Quick Scan frame
        self.create_quick_add_frame()
        self.create_view_frame()

        # Colonne droite
        self.right_column = QWidget()
        self.right_layout = QVBoxLayout(self.right_column)
        self.right_layout.setSpacing(20)
        self.sections_layout.addWidget(self.right_column, stretch=1)
        self.create_button_frame()
        self.create_stats_frame()


    # -------------------------
    # Quick Scan
    # -------------------------
    def create_quick_add_frame(self):
        # === 🧭 Cadre principal ===
        file_frame = ShadowFrame()
        file_frame.apply_shadow_style()
        self.left_layout.addWidget(file_frame)

        main_layout = QVBoxLayout(file_frame)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # === 📂 Ligne chemin + bouton de sélection ===
        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("No folder selected")
        self.path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #F7FAFC;
                border: 2px solid #3342CC;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: #2D3748;
            }
            QLineEdit:focus {
                border-color: #2B6CB0;
            }
        """)

        self.folder_btn = QPushButton("Browse Folders")
        self.folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_btn.setFixedWidth(160)
        self.folder_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A237E;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0D174D;
            }
            QPushButton:pressed {
                background-color: #060B2B;
            }
        """)
        self.folder_btn.clicked.connect(self.add_folder)

        path_layout.addWidget(self.path_edit, stretch=1)
        path_layout.addWidget(self.folder_btn, stretch=0)
        main_layout.addLayout(path_layout)

        # === 🧱 Ligne des boutons d’action ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Fonction pour styliser les boutons
        def create_button(text, color="#1A237E", hover="#0D174D", callback=None):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setMinimumHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 15px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    background-color: #060B2B;
                }}
            """)
            if callback:
                btn.clicked.connect(callback)
            return btn

        self.addFolder_btn = create_button("➕ Add Folder to Database", color="#3342CC", hover="#2B3AA0")
        self.createFile_btn = create_button("📄 Create File", color="#3342CC", hover="#2B3AA0")
        self.showContent_btn = create_button(
            "📁 Show Folder Content",
            color="#283593",
            hover="#1E2B6B",
            callback=self.refresh_list  # 🔗 Connexion directe à ta fonction
        )

        button_layout.addWidget(self.addFolder_btn)
        button_layout.addWidget(self.createFile_btn)
        button_layout.addWidget(self.showContent_btn)

        main_layout.addLayout(button_layout)

    def add_folder (self):
        folder = QFileDialog.getExistingDirectory(window, "Select a folder ")
        if folder:
            try:
                self.path_edit.setText(f"{folder}")


            except Exception as error:
                QMessageBox.critical(window, "Erreur", f"Impossible to add folder :\n{error}")


    def create_view_frame(self):
        """Crée une zone d'affichage défilable pour voir les fichiers d'un dossier (ex: log.txt)."""
        # === 📦 Cadre principal ===
        view_frame = ShadowFrame()
        view_frame.apply_shadow_style()
        self.left_layout.addWidget(view_frame)

        layout = QVBoxLayout(view_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # === 🧾 Titre ===
        title_label = QLabel("📂 Folder File Viewer")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1A237E;")
        layout.addWidget(title_label)

        # === 🧱 ScrollArea ===
        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(45, 55, 72, 0.8);
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(74, 85, 104, 0.8);
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(113, 128, 150, 0.8);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # === 📜 Conteneur interne (scrollable) ===
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(6)

        self.history_scroll_area.setWidget(scroll_content)
        layout.addWidget(self.history_scroll_area)

        # === 🔄 Label de statut + bouton refresh ===
        control_layout = QHBoxLayout()
        self.stats_label = QLabel("No folder selected.")
        self.stats_label.setStyleSheet("color: #4A5568; font-size: 13px;")




        layout.addLayout(control_layout)

    def refresh_list(self):
        """Actualise la liste des fichiers dans la zone de scroll."""
        try:
            # 🔄 Nettoyage
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            folder_path = self.path_edit.text().strip()
            if not folder_path or not os.path.isdir(folder_path):
                self.stats_label.setText("❌ Please select a valid folder.")
                return

            files = os.listdir(folder_path)
            if not files:
                self.stats_label.setText("📭 Folder is empty.")
                return

            # 🧾 Ajout des fichiers dans la zone scrollable
            for file in sorted(files):
                item_label = QLabel(f"📄 {file}")
                item_label.setStyleSheet("""
                    QLabel {
                        background-color: #EDF2F7;
                        border: 1px solid #CBD5E0;
                        border-radius: 8px;
                        padding: 6px 10px;
                        color: #2D3748;
                    }
                    QLabel:hover {
                        background-color: #E2E8F0;
                    }
                """)
                self.scroll_layout.addWidget(item_label)

            self.stats_label.setText(f"✅ {len(files)} files loaded.")
        except Exception as error:
            self.stats_label.setText(f"⚠️ Error: {error}")

    def start_scan(self):
        print(get_mode())
        if get_mode()=="auto":

            QMessageBox.warning(self, "Erreur", "le mode est auto le scan.")
        else:
            print('Start scan ')
            print(get_mode())
    # -------------------------
    # Stats
    # -------------------------
    def create_stats_frame(self):
        scan_frame = ShadowFrame()
        scan_frame.apply_shadow_style()
        self.right_layout.addWidget(scan_frame)
        layout = QVBoxLayout(scan_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        label = QLabel()
        pixmap = QPixmap("logoApplication.png")

        pixmap = pixmap.scaled(
            500, 500,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.setStyleSheet("""
                 QPushButton{
                    background-color: #2301C0;
                    color: white; border-radius: 8px;
                    padding: 12px; font-size: 15px; font-weight: bold;
                }
                QPushButton :hover {
                        background-color: #120A37;
                    }
                """)

        self.scan_btn.clicked.connect(self.start_scan)
        layout.addWidget(label)
        layout.addWidget(self.scan_btn)

    def create_button_frame(self):
        button_frame = ShadowFrame()
        button_frame.apply_shadow_style()
        self.right_layout.addWidget(button_frame)
        layout = QVBoxLayout(button_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        Autoscan_title = QLabel("Auto scan status")
        Autoscan_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        Autoscan_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        Autoscan_title.setStyleSheet("color: black; background-color: transparent; padding: 0; margin: 0;border:none;")
        Autoscan_lastScan = QLabel("Disabled")
        if get_mode()== "manuel":
            Autoscan_lastScan.setText("🔴 Disabled")
            Autoscan_lastScan.setStyleSheet("color: red; background-color: transparent; padding: 0; margin: 0;border:none;")
        else:
            Autoscan_lastScan.setText("🟢 Running ...")
            Autoscan_lastScan.setStyleSheet("color: green ; background-color: transparent; padding: 0; margin: 0;border:none;")



        layout.addWidget(Autoscan_title)
        layout.addWidget(Autoscan_lastScan)

    def update_last_scan_display(self):
        last_scan_label = self.findChild(QLabel, "last_scan_label")
        if last_scan_label:
            last_scan_label.setText(f"Last Scan: {self.last_scan_time}")




# -------------------------
# Lancer l'application
# -------------------------
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ScanPage(username="Tester", email="tester@example.com")
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())
