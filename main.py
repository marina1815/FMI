# main.py
from core.integrity_monitoring import init_db, build_baseline_for_folder, check_integrity, start_monitoring, stop_monitoring
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QFileDialog, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer

def main():
    init_db()
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("FIM - File Integrity Monitor")
    window.setGeometry(200, 100, 900, 600)
    layout = QVBoxLayout(window)

    info_label = QLabel("🧭 Surveillance des dossiers critiques")
    layout.addWidget(info_label)
    list_widget = QListWidget(); layout.addWidget(list_widget)
    stats_label = QLabel(""); layout.addWidget(stats_label)

    def add_folder():
        folder = QFileDialog.getExistingDirectory(window, "Sélectionner un dossier à surveiller")
        if folder:
            build_baseline_for_folder(folder)
            QMessageBox.information(window, "Baseline créée", f"Le dossier '{folder}' est désormais surveillé.")
            refresh_list()

    add_btn = QPushButton("➕ Ajouter un dossier à surveiller")
    add_btn.clicked.connect(add_folder)
    layout.addWidget(add_btn)

    def refresh_list():
        list_widget.clear()
        ok, mod, sup, file_status = check_integrity()
        stats_label.setText(f"✅ OK: {ok} | ⚠️ Modifié: {mod} | ❌ Supprimé: {sup}")
        for path, state in file_status:
            list_widget.addItem(f"{state}  →  {path}")

    timer = QTimer()
    timer.timeout.connect(refresh_list)
    timer.start(5000)

    refresh_list()

    window.show()

    # start monitoring thread AFTER the window is shown
    start_monitoring()

    # ensure the monitor stops when window closes
    def on_close(event):
        stop_monitoring()
        event.accept()
    window.closeEvent = on_close

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
