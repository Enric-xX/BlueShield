import sys
import os
import json
import socket
import requests
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

# --- CONFIGURACIÓN DE HARDWARE (Para evitar pantalla en blanco) ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"

# --- GESTIÓN DE BASE DE DATOS DE USUARIOS ---
DB_PATH = "shield_database.json"

def get_stored_user():
    """Carga el usuario desde el archivo JSON si existe"""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_user(username, password):
    """Guarda el nuevo usuario en la base de datos"""
    with open(DB_PATH, "w") as f:
        json.dump({"user": username, "pass": password}, f)

# --- VENTANA DE LOGIN / REGISTRO ---
class AuthSystem(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield | Identity Vault")
        self.setFixedSize(350, 400)
        self.setStyleSheet("background-color: #0a0c10; color: white; font-family: 'Inter', sans-serif;")
        
        self.layout = QVBoxLayout()
        
        self.title = QLabel("🛡️ BLUE SHIELD")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #3081f7; margin: 20px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nombre de Operador")
        self.user_input.setStyleSheet("background: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 8px; color: white;")
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Clave Maestra")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("background: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 8px; color: white;")
        
        self.action_btn = QPushButton()
        self.action_btn.setStyleSheet("background: #3081f7; color: white; font-weight: bold; padding: 12px; border-radius: 8px; margin-top: 10px;")
        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.pass_input)
        self.layout.addWidget(self.action_btn)
        
        # Lógica: ¿Registrar o Loguear?
        self.stored_data = get_stored_user()
        if self.stored_data:
            self.action_btn.setText("INICIAR SESIÓN")
            self.action_btn.clicked.connect(self.handle_login)
        else:
            self.title.setText("CREAR CUENTA ELITE")
            self.action_btn.setText("CONFIGURAR OPERADOR")
            self.action_btn.clicked.connect(self.handle_register)
            
        self.setLayout(self.layout)

    def handle_login(self):
        if self.user_input.text() == self.stored_data['user'] and self.pass_input.text() == self.stored_data['pass']:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Acceso Denegado: Credenciales Incorrectas.")

    def handle_register(self):
        u, p = self.user_input.text(), self.pass_input.text()
        if u and p:
            save_user(u, p)
            QMessageBox.information(self, "Éxito", "Operador registrado. Reinicia para entrar.")
            sys.exit()
        else:
            QMessageBox.warning(self, "Error", "Debes rellenar ambos campos.")

# --- NAVEGADOR PRINCIPAL ---
class BlueShieldElite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield Elite | Desktop OS")
        self.resize(1300, 850)
        
        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda i: self.tabs.removeTab(i) if self.tabs.count() > 1 else None)
        self.setCentralWidget(self.tabs)

        # Toolbar Dark
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.setStyleSheet("""
            QMainWindow { background: #0d1117; }
            QToolBar { background: #161b22; border-bottom: 2px solid #3081f7; padding: 8px; }
            QLineEdit { background: #010409; color: #58a6ff; border-radius: 10px; padding: 6px; border: 1px solid #30363d; }
            QTabBar::tab { background: #1c2128; color: #8b949e; padding: 12px 20px; }
            QTabBar::tab:selected { background: #3081f7; color: white; }
        """)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("¿Qué protocolo vamos a auditar hoy, Enric?")
        self.url_bar.returnPressed.connect(self.navigate)
        
        toolbar.addAction("➕", lambda: self.add_new_tab(QUrl("https://grok.com"), "Grok AI"))
        toolbar.addWidget(self.url_bar)
        toolbar.addAction("📟 RED", self.show_network)

        # Cargar Grok por defecto
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")

    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        browser.setUrl(qurl)
        # Forzar que los links se abran en pestañas de nuestra App
        browser.page().createWindow = lambda _type: self.add_new_tab(QUrl(""), "Nueva")
        
        idx = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(idx)
        
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if self.tabs.currentWidget() == browser else None)
        browser.titleChanged.connect(lambda t, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), t[:15]))

    def navigate(self):
        u = QUrl(self.url_bar.text())
        if u.scheme() == "": u.setScheme("https")
        self.tabs.currentWidget().setUrl(u)

    def show_network(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try: public_ip = requests.get('https://api.ipify.org', timeout=3).text
        except: public_ip = "Offline"
        QMessageBox.information(self, "Auditoría de Red", f"User: Enric\nLocal IP: {local_ip}\nPublic IP: {public_ip}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    auth = AuthSystem()
    if auth.exec() == QDialog.DialogCode.Accepted:
        window = BlueShieldElite()
        window.show()
        sys.exit(app.exec())
