import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont, QPixmap, QAction
from PyQt6.QtCore import Qt
# sys.path.append(r'C:\Users\DELL\PycharmProjects\FMI\ui')
from .gui_home import MainPage
from core.email_sender import generate_code, send_code_confirmation_email, send_confirmation_email
from core.user_manager import hash_password, register_user, verify_login, reset_password, load_users


# =========================
# FENÊTRE PRINCIPALE
# =========================
class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Integrity Monitor")
        self.setGeometry(100, 100, 400, 400)
        self.is_dark_theme = False
        self.current_content = None

        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setSpacing(0)

        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.layout.addWidget(self.container, 1)

        self.showPage("login")
        self.apply_light_theme()

    # =========================
    # CHANGEMENT DE PAGE
    # =========================
    def showPage(self, page):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if page == "login":
            form = self.create_login_content()
            image = self.create_image_widget("img/sign.png", right=True)
            self.container_layout.addWidget(form)
            self.container_layout.addWidget(image)
        elif page == "signup":
            image = self.create_image_widget("img/sign.png", right=False)
            form = self.create_signup_content()
            self.container_layout.addWidget(image)
            self.container_layout.addWidget(form)
        elif page == "forgot":
            form = self.create_forget_content()
            image = self.create_image_widget("img/sign.png", right=True)
            self.container_layout.addWidget(form)
            self.container_layout.addWidget(image)

        elif page == "new_password":
            form = self.create_new_password_content()
            image = self.create_image_widget("img/sign.png", right=False)
            self.container_layout.addWidget(image)
            self.container_layout.addWidget(form)


        elif page == "main":
            self.open_main_page()
            return

    # =========================
    # IMAGE WIDGET
    # =========================
    def create_image_widget(self, path, right=True):
        label = QLabel()
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(500, 600, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("background-color: #000000;" if right else "background-color: #000000;")
        return label

    def toggle_password_visibility(self):
        """Afficher ou cacher le mot de passe du login."""
        if self.password_login.echoMode() == QLineEdit.EchoMode.Password:
            self.password_login.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_pwd_btn.setText("👁️")  # œil barré
        else:
            self.password_login.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_pwd_btn.setText("👁️")  # œil ouvert

    # =========================
    # LOGIN
    # =========================
    def create_login_content(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(15)
        self.theme_label = QLabel("☀️")
        self.theme_label.setFont(QFont("Segoe UI", 20))
        self.theme_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_label.mousePressEvent = self.toggle_theme
        layout.addWidget(self.theme_label)

        title = QLabel("Welcome back")
        subtitle = QLabel("Please enter your details")
        title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        subtitle.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)

        self.user_login = QLineEdit()
        self.user_login.setPlaceholderText("Email address")
        # ===== Champ mot de passe avec icône œil =====
        pwd_container = QWidget()
        pwd_layout = QHBoxLayout(pwd_container)
        pwd_layout.setContentsMargins(0, 0, 0, 0)
        pwd_layout.setSpacing(0)

        self.password_login = QLineEdit()
        self.password_login.setPlaceholderText("Password")
        self.password_login.setEchoMode(QLineEdit.EchoMode.Password)
        #self.password_login.setStyleSheet("border: #151B54; padding: 8px; font-size: 15px;")

        # 👁️ Bouton œil
        self.toggle_pwd_btn = QPushButton("👁️")
        self.toggle_pwd_btn.setFixedWidth(40)
        self.toggle_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_pwd_btn.setStyleSheet("border: none; background: transparent; font-size: 16px;")
        self.toggle_pwd_btn.clicked.connect(self.toggle_password_visibility)

        pwd_layout.addWidget(self.password_login)
        pwd_layout.addWidget(self.toggle_pwd_btn)

        pwd_container.setStyleSheet("""
            QWidget {
                 border-radius: 6px;
            padding: 10px; font-size: 15px;  
            }
            QWidget:focus { border: 1px solid #151B54; }

        """)

        layout.addWidget(self.user_login)
        layout.addWidget(pwd_container)

        forgot = QLabel("<a href='#'>Forgot password?</a>")
        forgot.setTextFormat(Qt.TextFormat.RichText)
        forgot.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        forgot.linkActivated.connect(lambda _: self.showPage("forgot"))

        layout.addWidget(forgot, alignment=Qt.AlignmentFlag.AlignRight)

        signin_btn = QPushButton("Sign in")
        signin_btn.setObjectName("blueButton")
        signin_btn.clicked.connect(self.handle_login)

        layout.addWidget(signin_btn)
        layout.addSpacing(10)

        footer = QLabel("Don’t have an account? <a href='#'>Sign up</a>")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setTextFormat(Qt.TextFormat.RichText)
        footer.linkActivated.connect(lambda _: self.showPage("signup"))
        layout.addWidget(footer)

        return widget

    def create_forget_content(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(15)

        title = QLabel("Forgot Password?")
        subtitle = QLabel("Enter your email to reset your password")
        title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        subtitle.setFont(QFont("Segoe UI", 11))
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)

        self.forgot_email = QLineEdit()
        self.forgot_email.setPlaceholderText("Email address")
        layout.addWidget(self.forgot_email)

        send_btn = QPushButton("Send Code")
        send_btn.setObjectName("blueButton")
        send_btn.clicked.connect(self.handle_forgot_password)
        layout.addWidget(send_btn)

        back = QLabel("<a href='#'>Back to login</a>")
        back.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back.setTextFormat(Qt.TextFormat.RichText)
        back.linkActivated.connect(lambda _: self.showPage("login"))
        layout.addWidget(back)

        return widget

    def change_password(self):
        pwd = self.new_password_login.text()
        confirm = self.new_password_confirm.text()

        if not pwd or not confirm:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir les deux champs.")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return

        success, msg = reset_password(self.reset_email, pwd)
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.showPage("login")
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def create_new_password_content(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(15)

        title = QLabel("Reset Password")
        subtitle = QLabel("Enter your new password")
        title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        subtitle.setFont(QFont("Segoe UI", 11))
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)

        self.new_password_login = QLineEdit()
        self.new_password_login.setPlaceholderText("New password")
        self.new_password_login.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password_confirm = QLineEdit()
        self.new_password_confirm.setPlaceholderText("Confirm password")
        self.new_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.new_password_login)
        layout.addWidget(self.new_password_confirm)

        change_btn = QPushButton("Change Password")
        change_btn.setObjectName("blueButton")
        change_btn.clicked.connect(self.change_password)
        layout.addWidget(change_btn)

        return widget

    # =========================
    # SIGNUP
    # =========================
    def create_signup_content(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(15)

        self.theme_label = QLabel("☀️")
        self.theme_label.setFont(QFont("Segoe UI", 20))
        self.theme_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_label.mousePressEvent = self.toggle_theme
        layout.addWidget(self.theme_label)

        title = QLabel("Create an account")
        subtitle = QLabel("Please fill in your details")
        title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        subtitle.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(25)

        self.user_signup = QLineEdit()
        self.user_signup.setPlaceholderText("Username")
        self.mail_signup = QLineEdit()
        self.mail_signup.setPlaceholderText("Email address")
        self.password_signup = QLineEdit()
        self.password_signup.setPlaceholderText("Password")
        self.password_signup.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirm = QLineEdit()
        self.password_confirm.setPlaceholderText("Confirm password")
        self.password_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.user_signup)
        layout.addWidget(self.mail_signup)
        layout.addWidget(self.password_signup)
        layout.addWidget(self.password_confirm)

        signup_btn = QPushButton("Sign up")
        signup_btn.setObjectName("blueButton")
        signup_btn.clicked.connect(self.handle_signup)
        layout.addWidget(signup_btn)

        footer = QLabel("Already have an account? <a href='#'>Sign in</a>")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setTextFormat(Qt.TextFormat.RichText)
        footer.linkActivated.connect(lambda _: self.showPage("login"))
        layout.addWidget(footer)

        return widget

    # =========================
    # GESTION SIGNUP
    # =========================
    def handle_signup(self):
        username = self.user_signup.text().strip()
        email = self.mail_signup.text().strip()
        pwd = self.password_signup.text()
        confirm = self.password_confirm.text()

        if not username or not email or not pwd or not confirm:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return

        code = generate_code()
        success = send_code_confirmation_email(email, username, code)
        if not success:
            QMessageBox.critical(self, "Erreur", "Impossible d’envoyer l’e-mail. Vérifie ta connexion.")
            return

        user_code, ok = QInputDialog.getText(self, "Confirmation", f"Un code a été envoyé à {email}. Entrez-le ici :")
        if ok:
            if user_code.strip() == code:

                password_hash = hash_password(pwd)
                saved = register_user(username, email, password_hash)

                if not saved:
                    QMessageBox.warning(self, "Erreur", "Un compte existe déjà avec cet e-mail.")
                    return

                # ✅ Envoi de mail de bienvenue (optionnel)
                send_confirmation_email(email, username)

                QMessageBox.information(self, "Succès", "✅ Compte créé avec succès !")
                self.showPage("login")

            else:
                QMessageBox.critical(self, "Erreur", "Code incorrect.")

    def handle_login(self):
        email = self.user_login.text().strip()
        password = self.password_login.text()

        if not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        success, message = verify_login(email, password)

        if success:
            QMessageBox.information(self, "Connexion réussie", message)
            self.showPage("main")
        else:
            QMessageBox.critical(self, "Erreur", message)

    def handle_forgot_password(self):
        email = self.forgot_email.text().strip()
        users = load_users()

        if not email:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer votre adresse e-mail.")
            return
        if email not in users:
            QMessageBox.warning(self, "Erreur", "Aucun compte trouvé avec cet e-mail.")
            return

        # Génération du code
        code = generate_code()
        sent = send_code_confirmation_email(email, users[email]["username"], code)
        if not sent:
            QMessageBox.critical(self, "Erreur", "Impossible d’envoyer le code. Vérifie ta connexion.")
            return

        # Demander le code à l’utilisateur
        user_code, ok = QInputDialog.getText(self, "Vérification", f"Un code a été envoyé à {email}. Entrez-le ici :")
        if not ok or user_code.strip() != code:
            QMessageBox.critical(self, "Erreur", "❌ Code incorrect.")
            return

        # Si code valide → afficher page de changement de mot de passe
        self.reset_email = email  # sauvegarde pour la suite
        self.showPage("new_password")

    """def open_main_page(self):
        self.main_page = MainPage(self.is_dark_theme)
        self.setCentralWidget(self.main_page)"""

    def open_main_page(self):
        """Load the main dashboard inside the same window without resizing."""
        self.container.hide()  # Hide login/signup container
        self.main_page = MainPage(self.is_dark_theme)
        self.layout.addWidget(self.main_page)
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
        self.window().showMaximized()

    # =========================
    # THEMES
    # =========================
    def toggle_theme(self, event):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.apply_dark_theme()
            self.theme_label.setText("🌙")
        else:
            self.apply_light_theme()
            self.theme_label.setText("☀️")

    def apply_light_theme(self):
        self.setStyleSheet("""
        QMainWindow { background: white; }

        QLineEdit {
            border: 1px solid #ccc; border-radius: 6px;
            padding: 10px; font-size: 15px;
        }
        QLineEdit:focus { border: 1px solid #151B54; }
        QPushButton#blueButton {
            background-color: #151B54;
            color: white; border-radius: 8px;
            padding: 12px; font-size: 15px; font-weight: bold;
        }
        QPushButton#blueButton:hover {
            background-color: #120A37;
        }
        QLabel a { color: #151B54; text-decoration: none; }
        QLabel a:hover { text-decoration: underline; }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QMainWindow { background: #1e1e1e; }
        QLabel { color: white; }
        QLineEdit {
            background: #2d2d2d; color: white;
            border: 1px solid #555; border-radius: 6px;
            padding: 10px;font-size: 15px;
        }
         QLineEdit:focus { border: 1px solid #151B54; }
        QPushButton#blueButton {
            background-color: #151B54;
            color: black; border-radius: 8px;
            padding: 12px; font-weight: bold;font-size: 15px;
        }
        QPushButton#blueButton:hover {
            background-color: #120A37;
        }
        """)
