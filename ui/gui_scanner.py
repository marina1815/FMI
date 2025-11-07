import os
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPainter, QColor
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QDateTime, pyqtProperty
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
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

class scanPage(QWidget):
    def __init__(self, is_dark_theme=False, username=None, email=None):
        super().__init__()
        self.is_dark_theme = is_dark_theme
        self.username = username
        self.email = email
        self.last_scan_time = "Never"
        self.history_items = []

        self.apply_window_style()
        self.create_main_layout()
        self.create_main_content()

        self.update_scan_history_display()

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

        # History frame
        self.create_history_frame()

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
        # Create the frame
        file_frame = ShadowFrame()
        file_frame.apply_shadow_style()
        self.left_layout.addWidget(file_frame)

        frame_layout = QHBoxLayout(file_frame)
        frame_layout.setContentsMargins(20, 10, 20, 10)
        frame_layout.setSpacing(10)
        frame_layout.addStretch()
        pathSelector = QLineEdit()
        frame_layout.addWidget(pathSelector)


    def add_folder (self):
        folder = QFileDialog.getExistingDirectory(window, "Select a folder to monitor")
        if folder:
            try:
                build_baseline_for_folder(folder)

            except Exception as error:
                QMessageBox.critical(window, "Erreur", f"Impossible to add folder :\n{error}")



    # -------------------------
    # History
    # -------------------------
    def create_history_frame(self):
        history_frame = ShadowFrame()
        history_frame.apply_shadow_style()
        self.left_layout.addWidget(history_frame)
        layout = QVBoxLayout(history_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setWidgetResizable(True)
        layout.addWidget(self.history_scroll_area)

        self.history_content = QWidget()
        self.history_content_layout = QVBoxLayout(self.history_content)
        self.history_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.history_scroll_area.setWidget(self.history_content)

    # -------------------------
    # Stats
    # -------------------------
    def create_stats_frame(self):
        stats_frame = ShadowFrame()
        stats_frame.apply_shadow_style()
        self.right_layout.addWidget(stats_frame)
        layout = QVBoxLayout(stats_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        label = QLabel("File status overview")
        layout.addWidget(label)
        layout.addStretch()

    def create_button_frame(self):
        button_frame = ShadowFrame()
        button_frame.apply_shadow_style()
        self.right_layout.addWidget(button_frame)
        layout = QHBoxLayout(button_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        addFolder_btn = QPushButton("Add Folder")
        addFolder_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        addFolder_btn.clicked.connect(self.add_folder)
        layout.addWidget(addFolder_btn)
        layout.addStretch()
        createFile_btn = QPushButton("Create file ")
        createFile_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        createFile_btn.clicked.connect(self.add_folder)
        layout.addWidget(createFile_btn)




    def update_last_scan_display(self):
        last_scan_label = self.findChild(QLabel, "last_scan_label")
        if last_scan_label:
            last_scan_label.setText(f"Last Scan: {self.last_scan_time}")


    def update_scan_history_display(self):
        for i in reversed(range(self.history_content_layout.count())):
            widget = self.history_content_layout.itemAt(i).widget()
            if widget:
                self.history_content_layout.removeWidget(widget)
                widget.deleteLater()
        label = QLabel("No scan history available")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_content_layout.addWidget(label)

# -------------------------
# Lancer l'application
# -------------------------
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = scanPage(username="Tester", email="tester@example.com")
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())
