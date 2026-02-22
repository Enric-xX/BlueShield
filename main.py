import sys
import os
import json
import socket
import requests
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

# --- FIX PANTALLA BLANCA ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"

DB_FILE = "shield_db.json"

class BlueShieldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield Elite | Desktop OS")
        self.resize(1300, 850)
        self.showMaximized()

        # --- SISTEMA DE LOGIN / BASE DE DATOS ---
        self.auth_success = False
        self.check_auth()

    def check_auth(self):
        if not os.path.exists(DB_FILE):
            user, ok1 = QInputDialog.getText(self, 'Registro', 'Crea tu Usuario:')
            pw, ok2 = QInputDialog.getText(self, 'Registro', 'Crea tu Contraseña:', QLineEdit.EchoMode.Password)
            if ok1 and ok2:
                with open(DB_FILE, "w") as f:
                    json.dump({"u": user, "p": pw}, f)
                QMessageBox.information(self, "Éxito", "Usuario registrado. Reinicia la App.")
                sys.exit()
        
        # Login
        val_pw, ok = QInputDialog.getText(self, 'Auth', 'Introduce tu Clave Maestra:', QLineEdit.EchoMode.Password)
        if ok:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if val_pw == data['p']:
                    self.init_ui()
                else:
                    QMessageBox.critical(self, "Error", "Clave incorrecta")
                    sys.exit()
        else:
            sys.exit()

    def init_ui(self):
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda i: self.tabs.removeTab(i) if self.tabs.count() > 1 else None)
        self.setCentralWidget(self.tabs)

        # Toolbar
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("¿Qué protocolo vamos a auditar hoy, Enric?")
        self.url_bar.returnPressed.connect(self.navigate)

        nav_bar.addAction("🏠", self.add_home)
        nav_bar.addAction("➕", lambda: self.add_new_tab(QUrl("https://search.brave.com"), "Nueva"))
        nav_bar.addWidget(self.url_bar)
        nav_bar.addAction("📟 RED", self.show_stats)

        # CSS Dark Premium
        self.setStyleSheet("""
            QMainWindow { background: #0a0c10; }
            QToolBar { background: #161b22; border-bottom: 2px solid #3081f7; padding: 8px; spacing: 10px; }
            QLineEdit { background: #010409; color: #58a6ff; border-radius: 12px; padding: 8px; border: 1px solid #30363d; font-family: 'Consolas'; }
            QTabBar::tab { background: #1c2128; color: #8b949e; padding: 12px 25px; border-right: 1px solid #0d1117; }
            QTabBar::tab:selected { background: #3081f7; color: white; font-weight: bold; }
        """)

        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")

    def add_home(self):
        self.add_new_tab(QUrl("https://search.brave.com"), "Inicio")

    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        # ESTO ES LO QUE HACE QUE LOS LINKS SE ABRAN DENTRO Y NO EN CHROME
        browser.page().createWindow = lambda _type: self.add_new_tab(QUrl(""), "Nueva")
        
        browser.setUrl(qurl)
        idx = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(idx)
        
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if self.tabs.currentWidget() == browser else None)
        browser.titleChanged.connect(lambda t, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), t[:15]))

    def navigate(self):
        u = QUrl(self.url_bar.text())
        if u.scheme() == "": u.setScheme("https")
        self.tabs.currentWidget().setUrl(u)

    def show_stats(self):
        host = socket.gethostname()
        local_ip = socket.gethostbyname(host)
        try: pub_ip = requests.get('https://api.ipify.org').text
        except: pub_ip = "Error"
        QMessageBox.information(self, "Red", f"USER: Enric\nLOCAL: {local_ip}\nPUBLIC: {pub_ip}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BlueShieldApp()
    win.show()
    sys.exit(app.exec())
