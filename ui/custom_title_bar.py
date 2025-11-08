# ui/custom_title_bar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("""
           QWidget{
           border: none;
           }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d1cfcf;
            }
        """)

        # --- Logo + texte FortiFile ---
        self.logo = QLabel()
        pixmap = QPixmap("img/iconFortiFile.png").scaled(
            38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.logo.setPixmap(pixmap)

        self.title = QLabel("FortiFile")
        self.title.setFont(QFont("Segoe UI Light", 16, QFont.Weight.Bold))
        self.title.setStyleSheet("color: Black;")

        # --- Boutons à droite (avec icônes) ---
        self.btn_notify = QPushButton()
        self.btn_minimize = QPushButton()
        self.btn_maximize = QPushButton()
        self.btn_close = QPushButton()
        self.btn_mode = QPushButton()

        self.btn_notify.setIcon(QIcon("img/bell.png"))
        self.btn_minimize.setIcon(QIcon("img/minus.png"))
        self.btn_maximize.setIcon(QIcon("img/maximize.png"))
        self.btn_close.setIcon(QIcon("img/close.png"))
        self.btn_mode.setIcon(QIcon("img/light.png"))

        for btn in [self.btn_notify, self.btn_minimize, self.btn_maximize, self.btn_close, self.btn_mode]:
            btn.setFixedSize(20, 20)
            btn.setIconSize(btn.size())

        # Connexions
        self.btn_close.clicked.connect(self.parent.close)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        self.btn_minimize.clicked.connect(self.minimize_window)
        self.btn_notify.clicked.connect(self.show_notification)
        if hasattr(self.parent, 'toggle_theme'):
            self.btn_mode.clicked.connect(self.parent.toggle_theme)

        # --- Layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btn_mode)
        layout.addWidget(self.btn_notify)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def minimize_window(self):
        self.parent.showMinimized()

    def show_notification(self):
        print("🔔 Notification cliquée !")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent.move(self.parent.pos() + event.globalPosition().toPoint() - self.drag_position)
            self.drag_position = event.globalPosition().toPoint()