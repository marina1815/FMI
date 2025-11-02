import sys
from PyQt6.QtGui import QFont, QPixmap, QFontDatabase
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from ui.gui import MainPage


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File integrity monitor")
        self.setGeometry(200, 50, 1000, 750)
        self.is_dark_theme = False
        self.current_content = None  # Pour stocker le contenu actuel

        font_id = QFontDatabase.addApplicationFont("poppins/Poppins-SemiBold.ttf")
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            self.poppins_family = families[0] if families else None
        else:
            self.poppins_family = None

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)  # ✅ Stocker la référence
        self.layout.setSpacing(0)

        # Header
        header = self.create_header()
        self.layout.addWidget(header)

        # Contenu initial
        self.showPage("login")

        self.apply_light_theme()

    def showPage(self, pageName):
        """Met à jour le contenu en fonction du nom de la page"""
        # Supprime l'ancien contenu s'il existe
        if self.current_content:
            self.layout.removeWidget(self.current_content)
            self.current_content.deleteLater()
            self.current_content = None

        match pageName:
            case "login":
                self.current_content = self.create_login_content()
            case "signup":
                self.current_content = self.create_signup_content()
            case "home":
                self.current_content = self.create_home_content()  # ✅ Créer cette méthode
            case "main":
                self.open_main_page()  # ✅ Ouvrir MainPage
                return  # ✅ Important : return pour ne pas ajouter de contenu
            case _:
                print(f"Page inconnue: {pageName}")
                return

        # Ajoute le nouveau contenu seulement si ce n'est pas "main"
        if pageName != "main":
            self.layout.addWidget(self.current_content, 1)


    def create_header(self):
        """Crée le header avec icône, titre et bouton theme"""
        header = QWidget()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        pixmap = QPixmap("database-security.png").scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

        self.title_label = QLabel("File integrity monitor")
        self.title_label.setObjectName("headerTitle")

        left_layout.addWidget(self.icon_label)
        left_layout.addWidget(self.title_label)

        # Right section: theme button
        self.theme_pixmap = QPixmap("moon.png").scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
        self.theme_label = QLabel()
        self.theme_label.setPixmap(self.theme_pixmap)
        self.theme_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_label.mousePressEvent = self.toggle_theme

        header_layout.addWidget(left_widget)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_label)

        return header

    def create_login_content(self):
        """Crée le contenu pour le login"""
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(0)

        form_container = QWidget()
        form_container.setFixedSize(400, 400)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(40, 40, 40, 40)

        login_title = QLabel("Login to your account")
        login_title.setObjectName("loginTitle")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        username_container = QWidget()
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)

        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")

        self.user_login = QLineEdit()
        self.user_login.setPlaceholderText("Enter your username")
        self.user_login.setFixedHeight(45)

        username_layout.addWidget(username_label)
        username_layout.addWidget(self.user_login)

        password_container = QWidget()
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)

        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")

        self.password_login = QLineEdit()
        self.password_login.setPlaceholderText("Enter your password")
        self.password_login.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_login.setFixedHeight(45)

        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_login)

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 20, 0, 0)

        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setObjectName("loginButton")
        self.login_btn.clicked.connect(lambda: self.showPage("main"))  # ✅ Aller à MainPage

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setFixedHeight(45)
        self.signup_btn.setObjectName("signupButton")
        self.signup_btn.clicked.connect(lambda: self.showPage("signup"))

        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.signup_btn)

        form_layout.addWidget(login_title)
        form_layout.addWidget(username_container)
        form_layout.addWidget(password_container)
        form_layout.addStretch()
        form_layout.addWidget(buttons_container)

        content_layout.addStretch()
        content_layout.addWidget(form_container, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch()

        return content

    def create_signup_content(self):
        """Crée le contenu pour l'inscription"""
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(0)

        form_container = QWidget()
        form_container.setFixedSize(400, 600)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(40, 40, 40, 40)

        signup_title = QLabel("Create Account")
        signup_title.setObjectName("loginTitle")
        signup_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        self.user_signup = QLineEdit()
        self.user_signup.setPlaceholderText("Enter your username")
        self.user_signup.setFixedHeight(45)

        email_label = QLabel("Email")
        email_label.setObjectName("fieldLabel")
        self.mail_signup = QLineEdit()
        self.mail_signup.setPlaceholderText("Enter your email")
        self.mail_signup.setFixedHeight(45)

        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        self.password_signup = QLineEdit()
        self.password_signup.setPlaceholderText("Enter your password")
        self.password_signup.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_signup.setFixedHeight(45)

        confirm_label = QLabel("Confirm Password")
        confirm_label.setObjectName("fieldLabel")
        self.password_confirm = QLineEdit()
        self.password_confirm.setPlaceholderText("Confirm your password")
        self.password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirm.setFixedHeight(45)

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 20, 0, 0)

        self.return_btn = QPushButton("Back to Login")
        self.return_btn.setFixedHeight(45)
        self.return_btn.setObjectName("signupButton")
        self.return_btn.clicked.connect(lambda: self.showPage("login"))

        self.create_account_btn = QPushButton("Create Account")
        self.create_account_btn.setFixedHeight(45)
        self.create_account_btn.setObjectName("loginButton")
        self.create_account_btn.clicked.connect(lambda: self.showPage("main"))  # ✅ Aller à MainPage

        buttons_layout.addWidget(self.return_btn)
        buttons_layout.addWidget(self.create_account_btn)

        form_layout.addWidget(signup_title)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.user_signup)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.mail_signup)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_signup)
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.password_confirm)
        form_layout.addStretch()
        form_layout.addWidget(buttons_container)

        content_layout.addStretch()
        content_layout.addWidget(form_container, 0, Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch()

        return content

    def create_home_content(self):
        """Crée une page home simple (optionnel)"""
        content = QWidget()
        layout = QVBoxLayout(content)

        label = QLabel("Welcome Home!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(lambda: self.showPage("login"))
        layout.addWidget(back_btn)

        return content

    def open_main_page(self):
        """Ouvre la MainPage"""
        self.main_page = MainPage(self.is_dark_theme, self.styleSheet())
        self.setCentralWidget(self.main_page)

    def toggle_theme(self, event):
        self.is_dark_theme = not self.is_dark_theme

        if self.is_dark_theme:
            self.apply_dark_theme()
            sun_pixmap = QPixmap("sun.png").scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
            self.theme_label.setPixmap(sun_pixmap)
        else:
            self.apply_light_theme()
            self.theme_label.setPixmap(self.theme_pixmap)

        # Mettre à jour le style de la main page si elle existe
        if hasattr(self, 'main_page'):
            self.main_page.current_style = self.styleSheet()
            self.main_page.is_dark_theme = self.is_dark_theme
            self.main_page.apply_styles()  # ✅ Appliquer les nouveaux styles

    def apply_light_theme(self):
        """Applique le thème clair"""
        style = """
        QMainWindow {
            background-color: #ffffff;
        }
        QLabel#headerTitle {
            color: #6A5FF5;
            font-size: 40px;
            font-weight: bold;
            margin-left: 10px;
        }
        QLabel#loginTitle {
            color: #2D3748;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        QLabel#fieldLabel {
            color: #4A5568;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        QLineEdit {
            background-color: #FFFFFF;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px 15px;
            color: #2D3748;
            font-size: 14px;
            selection-background-color: #6A5FF5;
        }
        QLineEdit:focus {
            border-color: #6A5FF5;
            background-color: #FFFFFF;
        }
        QLineEdit::placeholder {
            color: #A0AEC0;
            font-style: italic;
            font-size: 13px;
        }
        QPushButton#loginButton {
            background-color: #6A5FF5;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton#loginButton:hover {
            background-color: #5A4FDF;
        }
        QPushButton#loginButton:pressed {
            background-color: #4A3FCF;
        }
        QPushButton#signupButton {
            background-color: #FFFFFF;
            color: #6A5FF5;
            border: 2px solid #6A5FF5;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton#signupButton:hover {
            background-color: #F7FAFC;
            border-color: #5A4FDF;
        }
        QPushButton#signupButton:pressed {
            background-color: #EDF2F7;
        }
        """
        self.setStyleSheet(style)

    def apply_dark_theme(self):
        """Applique le thème sombre"""
        style = """
        QMainWindow {
            background-color: #1A202C;
        }
        QLabel#headerTitle {
            color: #9F7AEA;
            font-size: 40px;
            font-weight: bold;
            margin-left: 10px;
        }
        QLabel#loginTitle {
            color: #F7FAFC;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        QLabel#fieldLabel {
            color: #E2E8F0;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        QLineEdit {
            background-color: #2D3748;
            border: 2px solid #4A5568;
            border-radius: 8px;
            padding: 12px 15px;
            color: #F7FAFC;
            font-size: 14px;
            selection-background-color: #9F7AEA;
        }
        QLineEdit:focus {
            border-color: #9F7AEA;
            background-color: #2D3748;
        }
        QLineEdit::placeholder {
            color: #718096;
            font-style: italic;
            font-size: 13px;
        }
        QPushButton#loginButton {
            background-color: #9F7AEA;
            color: #1A202C;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton#loginButton:hover {
            background-color: #B794F4;
        }
        QPushButton#loginButton:pressed {
            background-color: #805AD5;
        }
        QPushButton#signupButton {
            background-color: transparent;
            color: #9F7AEA;
            border: 2px solid #9F7AEA;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton#signupButton:hover {
            background-color: rgba(159, 122, 234, 0.1);
            border-color: #B794F4;
        }
        QPushButton#signupButton:pressed {
            background-color: rgba(159, 122, 234, 0.2);
        }
        """
        self.setStyleSheet(style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = ModernWindow()
    window.show()

    sys.exit(app.exec())