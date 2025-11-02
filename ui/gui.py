import sys
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize


class MainPage(QWidget):
    def __init__(self, is_dark_theme=False, current_style=None):
        super().__init__()
        self.is_dark_theme = is_dark_theme
        self.current_style = current_style
        self.sidebar_expanded = False

        # Créer le layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Créer le contenu principal avec sidebar
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Ajouter la sidebar
        self.create_sidebar()
        self.content_layout.addWidget(self.sidebar)

        # Ajouter la zone de contenu principale
        self.create_main_content()
        self.content_layout.addWidget(self.main_content, 1)

        main_layout.addWidget(self.content_widget, 1)

        # Appliquer les styles
        self.apply_styles()

        QTimer.singleShot(500, self.ask_autostart_question)

    def apply_styles(self):
        """Applique tous les styles"""
        #self.apply_header_style()
        self.apply_sidebar_style()
        self.apply_main_content_style()

    def create_sidebar(self):
        """Crée une sidebar collapsible avec logo et titre"""
        self.sidebar = QWidget()
        self.sidebar.setMinimumWidth(100)
        self.sidebar.setMaximumWidth(350)
        self.sidebar.setFixedWidth(60)

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(8, 15, 8, 15)  # ⬅️ Marges réduites
        self.sidebar_layout.setSpacing(5)  # ⬅️ Espacement réduit

        # Section logo + titre
        self.create_sidebar_header()
        self.sidebar_layout.addWidget(self.sidebar_header)

        # Boutons de navigation
        self.create_sidebar_buttons()
        self.sidebar_layout.addStretch()
        self.show_sidebar_text(False)

    def create_sidebar_header(self):
        """Crée l'en-tête de la sidebar avec logo et titre"""
        self.sidebar_header = QWidget()
        sidebar_header_layout = QHBoxLayout(self.sidebar_header)
        sidebar_header_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_header_layout.setSpacing(10)

        # Logo (non cliquable)
        self.logo_label = QLabel()
        pixmap = QPixmap("database-security.png").scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setFixedSize(32, 32)
        self.logo_label.setStyleSheet("background-color: transparent; border: none;")  # ⬅️ Assurer la transparence

        # Titre avec la même police que UI.py
        self.title_label = QLabel("File Integrity Monitor")
        self.title_label.setFont(QFont("Poppins", 14, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet(
            "color: white; background-color: transparent; border: none;")  # ⬅️ Supprimer bordures
        self.title_label.setWordWrap(True)

        sidebar_header_layout.addWidget(self.logo_label)
        sidebar_header_layout.addWidget(self.title_label)

    def toggle_sidebar(self):
        """Bascule l'état de la sidebar"""
        self.sidebar_expanded = not self.sidebar_expanded

        # Animations
        self.animation_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation_max = QPropertyAnimation(self.sidebar, b"maximumWidth")

        for anim in (self.animation_min, self.animation_max):
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuart)

        if self.sidebar_expanded:
            self.animation_min.setStartValue(60)
            self.animation_min.setEndValue(280)  # ⬅️ Largeur augmentée
            self.animation_max.setStartValue(60)
            self.animation_max.setEndValue(280)  # ⬅️ Largeur augmentée
            self.animation_max.finished.connect(lambda: self.show_sidebar_text(True))
        else:
            self.show_sidebar_text(False)
            self.animation_min.setStartValue(280)  # ⬅️ Largeur augmentée
            self.animation_min.setEndValue(60)
            self.animation_max.setStartValue(280)  # ⬅️ Largeur augmentée
            self.animation_max.setEndValue(60)

        self.animation_min.start()
        self.animation_max.start()

    def show_sidebar_text(self, show):
        """Affiche ou masque le texte dans la sidebar"""
        try:
            buttons = [self.dashboard_btn, self.scan_btn, self.history_btn, self.settings_btn, self.help_btn]
            icons = ["📊", "🔍", "📋", "⚙️", "❓"]
            texts = ["Dashboard", "Scanner", "History", "Parameters", "Help"]

            for i, btn in enumerate(buttons):
                if show:
                    btn.setText(f"{icons[i]} {texts[i]}")
                else:
                    btn.setText(icons[i])

            # Afficher/masquer le titre
            self.title_label.setVisible(show)

        except Exception as e:
            print(f"Error in show_sidebar_text: {e}")

    def create_sidebar_buttons(self):
        """Crée les boutons de la sidebar avec icônes et texte"""
        self.dashboard_btn = self.create_nav_button("📊")
        self.scan_btn = self.create_nav_button("🔍")
        self.history_btn = self.create_nav_button("📋")
        self.settings_btn = self.create_nav_button("⚙️")
        self.help_btn = self.create_nav_button("❓")

        for btn in [self.dashboard_btn, self.scan_btn, self.history_btn, self.settings_btn, self.help_btn]:
            self.sidebar_layout.addWidget(btn)


    def create_nav_button(self, icon):
        """Crée un bouton de navigation avec icône seulement"""
        button = QPushButton(icon)
        button.setFixedHeight(45)
        button.setFont(QFont("Segoe UI", 10))
        button.clicked.connect(self.toggle_sidebar)
        return button

    def create_main_content(self):
        """Crée la zone de contenu principale"""
        self.main_content = QWidget()
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(7, 7, 7, 7)
        main_layout.setSpacing(0)

        # Carte principale
        self.card = QWidget()
        self.card.setStyleSheet("""
            background-color: white;
            border-radius: 20px;
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(25)

        # === Titre du dashboard ===
        title = QLabel("📊 Dashboard – Surveillance en temps réel")
        title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #333;")
        card_layout.addWidget(title)

        # === Section Statistiques ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(25)

        self.card_files = self.create_stat_card("🗂️", "Fichiers surveillés", "152")
        self.card_suspects = self.create_stat_card("⚠️", "Fichiers suspects", "3")
        self.card_events = self.create_stat_card("📝", "Événements récents", "12")
        self.card_users = self.create_stat_card("👤", "Utilisateurs actifs", "1")

        stats_layout.addWidget(self.card_files)
        stats_layout.addWidget(self.card_suspects)
        stats_layout.addWidget(self.card_events)
        stats_layout.addWidget(self.card_users)

        # Animation d’apparition fluide
        for i, widget in enumerate([self.card_files, self.card_suspects, self.card_events, self.card_users]):
            anim = QPropertyAnimation(widget, b"windowOpacity")
            anim.setDuration(600 + i * 200)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            anim.start()

        card_layout.addLayout(stats_layout)

        # === Section graphique ou logs récents ===
        graph_section = QLabel("Graphiques et tendances à venir 📈")
        graph_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_section.setStyleSheet("color: gray; font-style: italic;")
        card_layout.addWidget(graph_section)

        main_layout.addWidget(self.card)

    def create_stat_card(self, emoji, title, value):
        """Crée une carte de statistique simple"""
        card = QWidget()
        card.setFixedHeight(110)
        card.setStyleSheet("""
            background-color: #F7FAFC;
            border-radius: 15px;
            border: 1px solid #E2E8F0;
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_icon = QLabel(emoji)
        label_icon.setFont(QFont("Segoe UI Emoji", 24))
        label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_title = QLabel(title)
        label_title.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        label_title.setStyleSheet("color: #4A5568;")
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_value = QLabel(value)
        label_value.setFont(QFont("Poppins", 18, QFont.Weight.Bold))
        label_value.setStyleSheet("color: #2D3748;")
        label_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label_icon)
        layout.addWidget(label_title)
        layout.addWidget(label_value)

        return card


    def apply_header_style(self):
        """Applique le style au header"""
        if self.is_dark_theme:
            self.header.setStyleSheet("""
                QWidget {
                    background-color: #1A202C;
                    border-bottom: 1px solid #4A5568;
                }
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #9F7AEA;
                    color: #1A202C;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #B794F4;
                }
                QPushButton:pressed {
                    background-color: #805AD5;
                }
                QPushButton#logoButton {
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.header.setStyleSheet("""
                QWidget {
                    background-color: #6A5FF5;
                    border-bottom: 1px solid #5A4FDF;
                }
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #FFFFFF;
                    color: #6A5FF5;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F7FAFC;
                }
                QPushButton:pressed {
                    background-color: #EDF2F7;
                }
                QPushButton#logoButton {
                    background-color: transparent;
                    border: none;
                }
            """)

    def apply_sidebar_style(self):
        """Applique le style à la sidebar"""
        if self.is_dark_theme:
            self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #2D3748;
                    border: none;  /* ⬅️ Supprimer la bordure droite */
                }
                QPushButton {
                    background-color: transparent;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    text-align: left;
                    padding: 12px 8px;
                    min-width: 40px;
                }
                QPushButton:hover {
                    background-color: #4A5568;
                }
                QPushButton:pressed {
                    background-color: #9F7AEA;
                    color: #1A202C;
                }
                QLabel {
                    background-color: transparent;  /* ⬅️ Fond transparent pour les labels */
                    border: none;  /* ⬅️ Supprimer les bordures des labels */
                }
            """)
        else:
            self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #6A5FF5;
                    border: none;  /* ⬅️ Supprimer la bordure droite */
                }
                QPushButton {
                    background-color: transparent;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    text-align: left;
                    padding: 12px 8px;
                    min-width: 40px;
                }
                QPushButton:hover {
                    background-color: #5A4FDF;
                }
                QPushButton:pressed {
                    background-color: #FFFFFF;
                    color: #6A5FF5;
                }
                QLabel {
                    background-color: transparent;  /* ⬅️ Fond transparent pour les labels */
                    border: none;  /* ⬅️ Supprimer les bordures des labels */
                }
            """)

    def apply_main_content_style(self):
        """Applique le style au contenu principal"""
        if self.is_dark_theme:
            self.main_content.setStyleSheet("""
                QWidget {
                    background-color: #1A202C;
                }
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                }
            """)
        else:
            self.main_content.setStyleSheet("""
                QWidget {
                    background-color: #6A5FF5;
                }
                QLabel {
                    color: #2D3748;
                    background-color: transparent;
                }
            """)

    def go_back(self):
        """Retourne à la page de login"""
        # Cette méthode sera connectée depuis la fenêtre principale
        pass

    def ask_autostart_question(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Paramètre de démarrage")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(
            "Souhaitez-vous autoriser le lancement automatique de l'application au démarrage de Windows "
            "afin d'assurer une surveillance continue de l'intégrité de vos fichiers et dossiers ?\n\n"
            "Vous pourrez également choisir de l'exécuter manuellement à tout moment."
        )

        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Activer le démarrage automatique")
        msg.button(QMessageBox.StandardButton.No).setText("Lancer manuellement")

        self.apply_theme_to_messagebox(msg)
        result = msg.exec()

        if result == QMessageBox.StandardButton.Yes:
            print("→ Lancement automatique activé")
            self.show_confirmation("Le démarrage automatique a été activé avec succès.")
        else:
            print("→ Mode manuel sélectionné")
            self.show_confirmation("Le mode manuel a été sélectionné.")

    def apply_theme_to_messagebox(self, msg_box):
        """Applique le thème approprié à la QMessageBox"""
        if self.is_dark_theme:
            dark_style = """
            QMessageBox {
                background-color: #1A202C;
                color: #F7FAFC;
            }
            QMessageBox QLabel {
                color: #F7FAFC;
            }
            QMessageBox QPushButton {
                background-color: #9F7AEA;
                color: #1A202C;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
            }
            QMessageBox QPushButton:hover {
                background-color: #B794F4;
            }
            QMessageBox QPushButton:pressed {
                background-color: #805AD5;
            }
            """
            msg_box.setStyleSheet(dark_style)
        else:
            light_style = """
            QMessageBox {
                background-color: #FFFFFF;
                color: #2D3748;
            }
            QMessageBox QLabel {
                color: #2D3748;
            }
            QMessageBox QPushButton {
                background-color: #6A5FF5;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5A4FDF;
            }
            QMessageBox QPushButton:pressed {
                background-color: #4A3FCF;
            }
            """
            msg_box.setStyleSheet(light_style)

    def show_confirmation(self, message):
        """Affiche une boîte de confirmation avec le thème approprié"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        self.apply_theme_to_messagebox(msg)
        msg.exec()