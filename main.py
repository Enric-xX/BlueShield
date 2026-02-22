import sys
import json
import os
import socket
import requests
import psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

# --- SISTEMA DE PERSISTENCIA ---
DB_FILE = "shield_config.json"

class ShieldAuth(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield | Auth")
        self.setFixedSize(350, 450)
        self.setStyleSheet("background-color: #0a0c10; color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        logo = QLabel("🛡️")
        logo.setStyleSheet("font-size: 60px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.info = QLabel("SISTEMA DE ACCESO ELITE")
        self.info.setStyleSheet("color: #3081f7; font-weight: bold;")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user = QLineEdit(); self.user.setPlaceholderText("Usuario")
        self.user.setStyleSheet("background: #161b22; padding: 10px; border-radius: 5px; border: 1px solid #30363d;")
        
        self.pw = QLineEdit(); self.pw.setPlaceholderText("Password")
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw.setStyleSheet("background: #161b22; padding: 10px; border-radius: 5px; border: 1px solid #30363d;")

        btn_login = QPushButton("ENTRAR")
        btn_login.setStyleSheet("background: #3081f7; font-weight: bold; padding: 10px;")
        btn_login.clicked.connect(self.auth_user)

        btn_reg = QPushButton("REGISTRAR NUEVO OPERADOR")
        btn_reg.setStyleSheet("background: transparent; color: #8b949e; font-size: 10px;")
        btn_reg.clicked.connect(self.register_user)

        layout.addWidget(logo); layout.addWidget(self.info)
        layout.addWidget(self.user); layout.addWidget(self.pw)
        layout.addWidget(btn_login); layout.addWidget(btn_reg)
        self.setLayout(layout)

    def auth_user(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if self.user.text() == data['u'] and self.pw.text() == data['p']:
                    self.accept()
                    return
        QMessageBox.warning(self, "Error", "Acceso denegado.")

    def register_user(self):
        with open(DB_FILE, "w") as f:
            json.dump({"u": self.user.text(), "p": self.pw.text()}, f)
        QMessageBox.information(self, "Éxito", "Operador registrado. Ya puedes Entrar.")

class BlueShieldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield OS | v4.0 Elite")
        self.resize(1300, 850)
        
        # UI TABS
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda i: self.tabs.removeTab(i) if self.tabs.count()>1 else None)
        self.setCentralWidget(self.tabs)

        # TOOLBAR
        self.tbar = QToolBar()
        self.addToolBar(self.tbar)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate)
        
        self.tbar.addAction("➕", self.add_new_tab)
        self.tbar.addWidget(self.url_bar)
        self.tbar.addAction("📟 INFO RED", self.show_network)

        self.setStyleSheet("""
            QMainWindow { background: #0d1117; }
            QToolBar { background: #161b22; border-bottom: 2px solid #3081f7; padding: 5px; }
            QLineEdit { background: #010409; color: #58a6ff; border-radius: 8px; padding: 5px; }
            QTabBar::tab { background: #1c2128; color: white; padding: 10px 20px; }
            QTabBar::tab:selected { background: #3081f7; font-weight: bold; }
        """)

        # Carga inicial: Varias pestañas a la vez
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")
        self.add_new_tab(QUrl("https://iplogger.org"), "IP Logger")

    def add_new_tab(self, qurl=None, label="Nueva"):
        if not qurl: qurl = QUrl("https://search.brave.com")
        browser = QWebEngineView()
        browser.setUrl(qurl)
        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()))
        browser.titleChanged.connect(lambda t, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), t[:15]))

    def show_network(self):
        # Función para ver IP Privada y Pública real
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try: public_ip = requests.get('https://api.ipify.org').text
        except: public_ip = "Offline"
        
        msg = f"--- AUDITORÍA DE RED BLUE SHIELD ---\n\n"
        msg += f"OPERADOR: Enric\n"
        msg += f"HOSTNAME: {hostname}\n"
        msg += f"IP PRIVADA (Local): {local_ip}\n"
        msg += f"IP PÚBLICA (Internet): {public_ip}\n"
        
        QMessageBox.information(self, "Protocolo de Red", msg)

    def navigate(self):
        u = QUrl(self.url_bar.text())
        if u.scheme() == "": u.setScheme("https")
        self.tabs.currentWidget().setUrl(u)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth = ShieldAuth()
    if auth.exec() == QDialog.DialogCode.Accepted:
        win = BlueShieldApp()
        win.show()
        sys.exit(app.exec())
