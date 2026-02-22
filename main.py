import sys
import os
import socket
# Intentamos importar requests, si falla usamos un plan B
try:
    import requests
except ImportError:
    print("Falta la librería 'requests'. Ejecuta: pip install requests")

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

# --- ARREGLO DE PANTALLA BLANCA ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"

class BlueShieldElite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield OS | Elite v4.2")
        self.resize(1200, 800)

        # 1. Pantalla de Login Simple integrada
        self.is_logged_in = False
        self.check_auth()

    def check_auth(self):
        password, ok = QInputDialog.getText(self, 'Blue Shield Auth', 'Introduce Clave de Operador:', QLineEdit.EchoMode.Password)
        if ok and password == '1234': # TU CONTRASEÑA ES 1234
            self.init_browser()
        else:
            sys.exit()

    def init_browser(self):
        # 2. Sistema de Pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda i: self.tabs.removeTab(i) if self.tabs.count() > 1 else None)
        self.setCentralWidget(self.tabs)

        # 3. Barra de herramientas
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("¿Qué protocolo vamos a auditar hoy, Enric?")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        toolbar.addAction("🏠", self.add_home_tab)
        toolbar.addAction("➕", lambda: self.add_new_tab(QUrl("https://search.brave.com"), "Nueva"))
        toolbar.addWidget(self.url_bar)
        toolbar.addAction("📟 RED", self.show_network)

        # Estilo Dark
        self.setStyleSheet("""
            QMainWindow { background: #0d1117; }
            QToolBar { background: #161b22; padding: 10px; border-bottom: 2px solid #3081f7; }
            QLineEdit { background: #010409; color: #58a6ff; border-radius: 10px; padding: 8px; border: 1px solid #30363d; }
            QTabBar::tab { background: #1c2128; color: white; padding: 10px 20px; }
            QTabBar::tab:selected { background: #3081f7; }
        """)

        # Pestañas iniciales
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")
        self.add_new_tab(QUrl("https://iplogger.org"), "IP Logger")

    def add_home_tab(self):
        self.add_new_tab(QUrl("https://search.brave.com"), "Inicio")

    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        # Esto evita que los links se abran fuera del programa
        browser.page().createWindow = lambda _type: self.add_new_tab(QUrl(""), "Nueva")
        
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if self.tabs.currentWidget() == browser else None)
        browser.titleChanged.connect(lambda t, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), t[:15]))

    def navigate_to_url(self):
        u = QUrl(self.url_bar.text())
        if u.scheme() == "": u.setScheme("https")
        self.tabs.currentWidget().setUrl(u)

    def show_network(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try:
            public_ip = requests.get('https://api.ipify.org').text
        except:
            public_ip = "Error"
        
        QMessageBox.information(self, "Red", f"Hostname: {hostname}\nLocal: {local_ip}\nPublic: {public_ip}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlueShieldElite()
    window.show()
    sys.exit(app.exec())
