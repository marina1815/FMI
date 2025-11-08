from PyQt6.QtWidgets import (
    QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont

from ui.gui_home import MainPage
from ui.gui_dashboard import DashboardPage
from ui.gui_scanner import ScanPage
from ui.profil import ProfileMenuMixin


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        print("🚀 AppWindow initialisée !")

        self.is_dark_theme = False
        self.sidebar_expanded = False

        # === Initialiser les pages ===
        self.home_page = None
        self.dashboard_page = None
        self.scan_page = None

        # === Layout principal ===
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # === Sidebar ===
        self.create_sidebar()

        # === Contenu principal (header + stack) ===
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Header
        #self.create_header()
        #self.content_layout.addWidget(self.header)

        # QStackedWidget
        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)

        # === Ajouter dans le layout principal ===
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_widget)

        # === Taille de fenêtre ===
        self.setMinimumSize(1000, 600)

        # === Charger la page d'accueil par défaut ===
        self.load_home("User")

    # =========================================================
    # 🔹 Création du header(profil)
    # =========================================================
    """
        def create_header(self):
        self.header = QWidget()
        self.header.setFixedHeight(self.scale_value(60, False))
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(
        self.scale_value(20),
        self.scale_value(10, False),
        self.scale_value(20),
        self.scale_value(10, False)
    )
        self.header_layout.addStretch()

        #self.profile_menu = self.create_profile_menu()
        
        # Mettre à jour le nom d'utilisateur dans le menu profil
        if hasattr(self, 'username') and self.username:
            self.set_username(self.username)
            """


    # =========================================================
    # 🔹 Création de la sidebar
    # =========================================================
    def create_sidebar(self):
        """Crée une sidebar collapsible avec tailles relatives"""
        self.sidebar = QWidget()
        self.sidebar.setMinimumWidth(self.scale_value(100))
        self.sidebar.setMaximumWidth(self.scale_value(100))
        self.sidebar.setFixedWidth(self.scale_value(100))
        self.apply_sidebar_style()

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(self.scale_value(20), 0, 0, 0)
        self.sidebar_layout.setSpacing(self.scale_value(10))
        #self.create_sidebar_logo()

        self.create_sidebar_buttons()

        self.sidebar_layout.addStretch()
        self.show_sidebar_text(False)

    def create_sidebar_buttons(self):
        """Crée les boutons de la sidebar avec icônes et texte"""
        self.sidebar_layout.addSpacing(self.scale_value(30, False))
        self.home_btn = self.create_nav_button("img/home.png", "Home", "home")
        self.scan_btn = self.create_nav_button("img/scanner.png", "Scan", "scanner")
        self.dashboard_btn = self.create_nav_button("img/dashboard.png", "Dashboard", "dashboard")
        self.identity_btn = self.create_nav_button("img/identity.png", "Identity", "identity")

        for btn in [self.home_btn, self.scan_btn,self.dashboard_btn, self.identity_btn]:
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addSpacing(self.scale_value(380, False))

        self.settings_btn = self.create_nav_button("img/setting.png", "Settings", "setting")
        self.help_btn = self.create_nav_button("img/question.png", "Help", "question")
        self.about_btn = self.create_nav_button("img/about.png", "About", "about")

        for btn in [self.settings_btn, self.help_btn, self.about_btn]:
            self.sidebar_layout.addWidget(btn)

        self.select_button(self.home_btn)

    def create_nav_button(self, icon_path, tooltip="", button_id=""):
        """Crée un bouton de navigation avec icône seulement"""
        button = QPushButton()
        button.setFixedHeight(self.scale_value(45, False))
        button.setFont(QFont("Segoe UI", self.scale_value(10)))
        button.setProperty("button_id", button_id)

        icon_size = self.scale_value(30)
        icon_pixmap = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
        button.setIcon(QIcon(icon_pixmap))
        button.setIconSize(QSize(icon_size, icon_size))
        button.clicked.connect(lambda checked, btn=button: self.on_nav_button_clicked(btn))
        button.clicked.connect(self.toggle_sidebar)
        return button

    def select_button(self, button):
        """Sélectionne un bouton et désélectionne les autres"""
        all_buttons = [self.home_btn, self.scan_btn,self.dashboard_btn, self.identity_btn,
                       self.settings_btn, self.help_btn, self.about_btn]

        for btn in all_buttons:
            self.deselect_button(btn)

        if self.is_dark_theme:
            button.setStyleSheet("""
                     QPushButton {
                         background-color:#525063;
                         color: #0D0422;
                         border: none;
                         border-radius: 5px;
                         font-weight: bold;
                         text-align: left;
                         padding: 10px 5px;
                         font-size: 16px;
                         width: 200px;
                         border-left: 4px solid #FFFFFF;
                         border-top-left-radius: 20px;
                         border-bottom-left-radius: 20px;
                         border-top-right-radius: 0px;
                         border-bottom-right-radius: 0px;
                         max-width: 220px;
                     }
                 """)
        else:
            button.setStyleSheet("""
                     QPushButton {
                         background-color:#DFDFED;
                         color: #151B54;
                         border: none;
                         border-radius: 5px;
                         font-weight: bold;
                         text-align: left;
                         padding: 10px 5px;
                         font-size: 16px;
                         width: 200px;
                         border-left: 4px solid #FFFFFF;
                         border-top-left-radius: 20px;
                         border-bottom-left-radius: 20px;
                         border-top-right-radius: 0px;
                         border-bottom-right-radius: 0px;
                         max-width: 220px;
                     }
                 """)

        button_id = button.property("button_id")
        colored_icon_path = f"img/{button_id}_selec.png"

        colored_pixmap = QPixmap(colored_icon_path)
        if not colored_pixmap.isNull():
            icon_size = self.scale_value(24)
            colored_pixmap = colored_pixmap.scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
            button.setIcon(QIcon(colored_pixmap))
        else:
            icon_size = self.scale_value(24)
            normal_icon_path = f"img/{button_id}.png"
            normal_pixmap = QPixmap(normal_icon_path).scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                             Qt.TransformationMode.SmoothTransformation)
            button.setIcon(QIcon(normal_pixmap))

        self.current_selected_button = button

    def deselect_button(self, button):
        button.setStyleSheet("""
                 QPushButton {
                     background-color: transparent;
                     color: #FFFFFF;
                     border: none;
                     border-radius: 5px;
                     font-weight: bold;
                     text-align: left;
                     padding: 10px 5px;
                     min-width: 100px;
                     width: 200px;
                     max-width: 200px;
                     font-size: 14px;
                 }
                 QPushButton:hover {
                     background-color: rgba(255, 255, 255, 0.1);
                     font-size: 14px;
                 }
             """)

        button_id = button.property("button_id")
        normal_icon_path = f"img/{button_id}.png"

        normal_pixmap = QPixmap(normal_icon_path)
        if not normal_pixmap.isNull():
            icon_size = self.scale_value(24)
            normal_pixmap = normal_pixmap.scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
            button.setIcon(QIcon(normal_pixmap))

    def show_sidebar_text(self, show):
        try:
            buttons = [self.home_btn,self.scan_btn, self.dashboard_btn, self.identity_btn,
                       self.settings_btn, self.help_btn, self.about_btn]
            icons = ["img/home.png","img/scanner.png", "img/dashboard.png", "img/identity.png",
                     "img/setting.png", "img/question.png", "img/about.png"]
            active_icons = ["img/home_selec.png","img/scanner_selec.png", "img/dashboard_selec.png", "img/identity_selec.png",
                            "img/setting_selec.png", "img/question_selec.png", "img/about_selec.png"]
            texts = [" Home","Scan"," Dashboard", " Identity", " Settings", " Help", " About"]

            icon_size = self.scale_value(24)
            for i, btn in enumerate(buttons):
                if show:
                    if hasattr(self, 'current_selected_button') and btn == self.current_selected_button:
                        icon_path = active_icons[i]
                    else:
                        icon_path = icons[i]

                    icon_pixmap = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation)
                    btn.setIcon(QIcon(icon_pixmap))
                    btn.setText(texts[i])
                    btn.setToolTip("")

                    if hasattr(self, 'current_selected_button') and btn == self.current_selected_button:
                        self.select_button(btn)
                else:
                    if hasattr(self, 'current_selected_button') and btn == self.current_selected_button:
                        icon_path = active_icons[i]
                    else:
                        icon_path = icons[i]

                    icon_pixmap = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation)
                    btn.setIcon(QIcon(icon_pixmap))
                    btn.setText("")
                    btn.setToolTip(texts[i].strip())

                    if hasattr(self, 'current_selected_button') and btn == self.current_selected_button:
                        self.select_button(btn)

        except Exception as e:
            print(f"Error in show_sidebar_text: {e}")

    def apply_sidebar_style(self):
        if self.is_dark_theme:
            self.sidebar.setStyleSheet("""
                     QWidget {
                         background-color: rgba(37, 37, 55, 0.7);
                         border-right: 1px solid #4A5568;
                     }
                     QPushButton {
                         background-color: transparent;
                         color: #FFFFFF;
                         border: none;
                         border-radius: 5px;
                         text-align: left;
                         padding: 10px;
                         padding: 10px 5px;
                         min-width: 40px;
                     }
                     QPushButton:hover {
                         background-color: #2D3748;
                     }
                     QPushButton:pressed {
                         background-color: #9F7AEA;
                         color: #1A202C;
                     }
                 """)
        else:
            self.sidebar.setStyleSheet("""
                     QWidget {
                         background-color: #151B54;
                         border-right: 1px solid #5A4FDF;
                     }
                     QLabel {
                         color: #FFFFFF;
                         background-color: transparent;
                         font-weight: bold;
                     }
                     QPushButton {
                         background-color: transparent;
                         color: #FFFFFF;
                         border: none;
                         border-radius: 5px;
                         text-align: left;
                         padding: 10px;
                         padding: 10px 5px;
                         min-width: 50px;
                     }
                     QPushButton:hover {
                         background-color: #5A4FDF;
                     }
                     QPushButton:pressed {
                         background-color: #FFFFFF;
                         color: #6A5FF5;
                     }
                 """)

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded

        self.animation_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation_max = QPropertyAnimation(self.sidebar, b"maximumWidth")

        for anim in (self.animation_min, self.animation_max):
            anim.setDuration(200)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuart)

        if self.sidebar_expanded:
            self.animation_min.setStartValue(self.scale_value(100))
            self.animation_min.setEndValue(self.scale_value(150))
            self.animation_max.setStartValue(self.scale_value(100))
            self.animation_max.setEndValue(self.scale_value(150))
            self.animation_max.finished.connect(lambda: self.show_sidebar_text(True))
        else:
            self.show_sidebar_text(False)
            self.animation_min.setStartValue(self.scale_value(150))
            self.animation_min.setEndValue(self.scale_value(100))
            self.animation_max.setStartValue(self.scale_value(150))
            self.animation_max.setEndValue(self.scale_value(100))

        self.animation_min.start()
        self.animation_max.start()
    # =========================================================
    # 🔹 Gestion des pages
    # =========================================================
    def load_home(self, username):
        print("Chargement de la page Home...")
        if self.home_page is None:
            self.home_page = MainPage(username=username, is_dark_theme=self.is_dark_theme)
            print("📦 Création de la page Home")
            self.stack.addWidget(self.home_page)
            print("✅ Page Home ajoutée au stack.")

        self.stack.setCurrentWidget(self.home_page)
        print(f"🏠 Page Home affichée pour {username}")

    def load_dashboard(self, username):
        print("Chargement de la page Dashboard...")
        if self.dashboard_page is None:
            self.dashboard_page = DashboardPage(username=username)
            print("📦 Création de la page Dashboard")
            self.stack.addWidget(self.dashboard_page)

        self.stack.setCurrentWidget(self.dashboard_page)
        print(f"📊 Page Dashboard affichée pour {username}")

    def load_scan(self, username):
        print("Chargement de la page Scan...")
        if self.scan_page is None:
            self.scan_page = ScanPage(username=username)
            print("📦 Création de la page Scan")
            self.stack.addWidget(self.scan_page)

        self.stack.setCurrentWidget(self.scan_page)
        print(f"🔍 Page Scan affichée pour {username}")

    # =========================================================
    # 🔹 Sélection bouton
    # =========================================================
    def on_nav_button_clicked(self, clicked_button):
        self.select_button(clicked_button)
        button_id = clicked_button.property("button_id")
        print(f"Bouton cliqué: {button_id}")

        # 🚀 Charger la page correspondante
        if button_id == "home":
            self.load_home(username="User")
        elif button_id == "scan":
            self.load_home(username="User")
        elif button_id == "dashboard":
            self.load_dashboard(username="User")
        elif button_id == "identity":
            self.load_home(username="User")  # ou créer une page Identity si elle existe
        elif button_id == "setting":
            print("Settings page pas encore implémentée")
        elif button_id == "question":
            print("Help page pas encore implémentée")
        elif button_id == "about":
            print("About page pas encore implémentée")

    def scale_value(self, value, is_width=True):
        """Calcule une valeur d'échelle relative à la taille de l'écran"""
        screen_size = self.screen().availableSize() if self.screen() else QSize(1200, 800)
        base_width = 1200
        base_height = 700

        if is_width:
            return int(value * screen_size.width() / base_width)
        else:
            return int(value * screen_size.height() / base_height)



