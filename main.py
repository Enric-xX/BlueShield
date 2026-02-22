import sys
import json
import socket
import requests
import psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

# --- BASE DE DATOS LOCAL ---
DB_PATH = "shield_vault.json"

def save_user(user, password):
    data = {"user": user, "password": password}
    with open(DB_PATH, "w") as f:
        json.dump(data, f)

def load_user():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return None

# --- PANTALLA DE INICIO DE SESIÓN / REGISTRO ---
class AuthSystem(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield | Security Access")
        self.setFixedSize(400, 550)
        self.setStyleSheet("background-color: #0a0c10; color: white; font-family: 'Segoe UI';")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Icono Pro
        self.logo = QLabel("🛡️")
        self.logo.setStyleSheet("font-size: 70px;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title = QLabel("BLUE SHIELD ELITE")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold; color: #3081f7; letter-spacing: 3px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText("Nombre de Operador")
        self.user_in.setStyleSheet("background: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 8px;")

        self.pass_in = QLineEdit()
        self.pass_in.setPlaceholderText("Clave Maestra")
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_in.setStyleSheet("background: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 8px;")

        self.btn_login = QPushButton("INICIAR PROTOCOLO")
        self.btn_login.setStyleSheet("background: #3081f7; font-weight: bold; padding: 15px; border-radius: 10px; margin-top: 10px;")
        self.btn_login.clicked.connect(self.login)

        self.btn_reg = QPushButton("CREAR NUEVA CUENTA")
        self.btn_reg.setStyleSheet("background: transparent; color: #8b949e; text-decoration: underline; border: none;")
        self.btn_reg.clicked.connect(self.register)

        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addSpacing(30)
        layout.addWidget(self.user_in)
        layout.addWidget(self.pass_in)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_reg)
        self.setLayout(layout)

    def login(self):
        saved = load_user()
        if saved and self.user_in.text() == saved['user'] and self.pass_in.text() == saved['password']:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Acceso no autorizado.")

    def register(self):
        if self.user_in.text() and self.pass_in.text():
            save_user(self.user_in.text(), self.pass_in.text())
            QMessageBox.information(self, "Éxito", "Cuenta creada. Ya puedes iniciar sesión.")
        else:
            QMessageBox.warning(self, "Error", "Rellena los campos para registrarte.")

# --- MÓDULO DE RED (IP PRIVADA, PÚBLICA, ETC) ---
class NetworkStats(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setStyleSheet("background: #010409; color: #00ff88; font-family: 'Consolas'; font-size: 14px; border: none;")
        layout.addWidget(self.info)
        self.setLayout(layout)
        self.refresh_stats()

    def refresh_stats(self):
        # IP Privada
        hostname = socket.gethostname()
        ip_privada = socket.gethostbyname(hostname)
        # IP Pública
        try:
            ip_publica = requests.get('https://api.ipify.org').text
        except:
            ip_publica = "Desconectado"
        
        stats = f"""
        [ BLUE SHIELD NETWORK AUDIT ]
        ----------------------------------
        HOSTNAME: {hostname}
        IP PRIVADA: {ip_privada}
        IP PÚBLICA: {ip_publica}
        
        [ INTERFACES DE RED ]
        """
        for interface, addrs in psutil.net_if_addrs().items():
            stats += f"\n- {interface}: {addrs[0].address}"
            
        self.info.setText(stats)

# --- VENTANA PRINCIPAL ---
class BlueShieldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield Elite | Terminal")
        self.resize(1280, 800)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate)
        
        nav_bar.addAction("➕", self.add_new_tab)
        nav_bar.addWidget(self.url_bar)
        nav_bar.addAction("📟 RED", self.add_network_tab)

        # Estilo
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QToolBar { background: #161b22; border-bottom: 2px solid #3081f7; padding: 10px; }
            QLineEdit { background: #010409; color: #58a6ff; border: 1px solid #30363d; padding: 8px; border-radius: 10px; }
            QTabBar::tab { background: #1c2128; color: white; padding: 12px; min-width: 120px; }
            QTabBar::tab:selected { background: #3081f7; }
        """)

        # Inicio
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")

    def add_new_tab(self, qurl=None, label="Nueva Pestaña"):
        if not qurl: qurl = QUrl("https://search.brave.com")
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda q, b=browser: self.url_bar.setText(q.toString()) if b == self.tabs.currentWidget() else None)

    def add_network_tab(self):
        self.tabs.addTab(NetworkStats(), "AUDITORÍA RED")
        self.tabs.setCurrentIndex(self.tabs.count()-1)

    def navigate(self):
        url = QUrl(self.url_bar.text())
        if url.scheme() == "": url.setScheme("https")
        self.tabs.currentWidget().setUrl(url)

    def close_tab(self, i):
        if self.tabs.count() > 1: self.tabs.removeTab(i)

import os
if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth = AuthSystem()
    if auth.exec() == QDialog.DialogCode.Accepted:
        window = BlueShieldApp()
        window.show()
        sys.exit(app.exec())
