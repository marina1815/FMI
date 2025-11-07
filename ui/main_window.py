# app_window.py
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from ui.gui_login import ModernWindow
from ui.gui_home import MainPage
from ui.gui_dashboard import DashboardPage

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FortiFile")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = ModernWindow()
        self.home_page = None
        self.dashboard_page = None

        self.stack.addWidget(self.login_page)

        # Connect login success
        self.login_page.login_success_callback = self.load_home

    def load_home(self, username):
        """Switch to home after login."""
        # If not created yet
        if self.home_page is None:
            self.home_page = MainPage(username=username, is_dark_theme=False)
            self.stack.addWidget(self.home_page)

            # ✅ Connect navigation callback once
            self.home_page.navigate_dashboard = lambda: self.load_dashboard(username)

        # Then show the home page
        self.stack.setCurrentWidget(self.home_page)

    def load_dashboard(self, username):
        """Switch to dashboard view."""
        if self.dashboard_page is None:
            self.dashboard_page = DashboardPage(username=username)
            self.stack.addWidget(self.dashboard_page)

        self.stack.setCurrentWidget(self.dashboard_page)
