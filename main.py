import sys
import os
import json
import socket
import requests
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

# --- 🛠️ SOLUCIÓN AL ERROR DE PANTALLA BLANCA ---
# Estas líneas desactivan la aceleración por hardware que causa el fallo en Windows
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

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
        logo.setStyleSheet("font-size: 60px; margin-top: 20px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.info = QLabel("SISTEMA DE ACCESO ELITE")
        self.info.setStyleSheet("color: #3081f7; font-weight: bold; font-size: 16px;")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user = QLineEdit(); self.user.setPlaceholderText("Nombre de Operador")
        self.user.setStyleSheet("background: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; color: white;")
        
        self.pw = QLineEdit(); self.pw.setPlaceholderText("Clave de Seguridad")
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw.setStyleSheet("background: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; color: white;")

        btn_login = QPushButton("INICIAR PROTOCOLO")
        btn_login.setStyleSheet("background: #3081f7; font-weight: bold; padding: 12px; border-radius: 8px;")
        btn_login.clicked.connect(self.auth_user)

        btn_reg = QPushButton("REGISTRAR NUEVO OPERADOR")
        btn_reg.setStyleSheet("background: transparent; color: #8b949e; font-size: 11px; text-decoration: underline; border: none;")
        btn_reg.clicked.connect(self.register_user)

        layout.addWidget(logo); layout.addWidget(self.info)
        layout.addSpacing(20)
        layout.addWidget(self.user); layout.addWidget(self.pw)
        layout.addWidget(btn_login); layout.addWidget(btn_reg)
        layout.addStretch()
        self.setLayout(layout)

    def auth_user(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if self.user.text() == data['u'] and self.pw.text() == data['p']:
                    self.accept()
                    return
        QMessageBox.warning(self, "Error", "Acceso denegado. Operador no reconocido.")

    def register_user(self):
        if self.user.text() and self.pw.text():
            with open(DB_FILE, "w") as f:
                json.dump({"u": self.user.text(), "p": self.pw.text()}, f)
            QMessageBox.information(self, "Éxito", "Operador registrado. Ya puedes Entrar.")

class BlueShieldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield OS | Elite v4.1")
        self.resize(1300, 850)
        
        # UI TABS
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # TOOLBAR
        self.tbar = QToolBar()
        self.addToolBar(self.tbar)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("¿Qué protocolo vamos a auditar hoy, Enric?")
        self.url_bar.returnPressed.connect(self.navigate)
        
        self.tbar.addAction("🏠", self.add_home_tab)
        self.tbar.addAction("➕", lambda: self.add_new_tab(QUrl("https://search.brave.com"), "Nueva"))
        self.tbar.addWidget(self.url_bar)
        self.tbar.addAction("📟 RED", self.show_network)

        self.setStyleSheet("""
            QMainWindow { background: #0d1117; }
            QToolBar { background: #161b22; border-bottom: 2px solid #3081f7; padding: 10px; spacing: 10px; }
            QLineEdit { background: #010409; color: #58a6ff; border-radius: 12px; padding: 8px; border: 1px solid #30363d; font-family: 'Consolas'; }
            QTabBar::tab { background: #1c2128; color: #8b949e; padding: 12px 20px; border-right: 1px solid #0d1117; min-width: 140px; }
            QTabBar::tab:selected { background: #3081f7; color: white; font-weight: bold; }
        """)

        # Abrir Grok y el Panel de Red al inicio
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")

    def add_home_tab(self):
        # Esta función cargaría tu buscador personalizado o una web limpia
        self.add_new_tab(QUrl("https://search.brave.com"), "Inicio")

    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        # Forzar que los links se abran AQUÍ y no en Chrome
        browser.page().createWindow = lambda _type: self.add_new_tab(QUrl(""), "Nueva")
        
        browser.setUrl(qurl)
        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)
        
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if self.tabs.currentWidget() == browser else None)
        browser.titleChanged.connect(lambda t, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), t[:15]))

    def show_network(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            public_ip = "No disponible (Sin internet)"
        
        msg = f"--- AUDITORÍA BLUE SHIELD ---\n\n"
        msg += f"OPERADOR: Enric\n"
        msg += f"HOSTNAME: {hostname}\n"
        msg += f"IP LOCAL: {local_ip}\n"
        msg += f"IP PÚBLICA: {public_ip}\n"
        QMessageBox.information(self, "Protocolo de Red", msg)

    def navigate(self):
        u = QUrl(self.url_bar.text())
        if u.scheme() == "": u.setScheme("https")
        self.tabs.currentWidget().setUrl(u)

    def close_tab(self, i):
        if self.tabs.count() > 1: self.tabs.removeTab(i)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth = ShieldAuth()
    if auth.exec() == QDialog.DialogCode.Accepted:
        win = BlueShieldApp()
        win.show()
        sys.exit(app.exec())
