import sys
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtGui import *

# --- CONFIGURACIÓN Y SEGURIDAD ---
USER_DATA_FILE = "shield_users.json"
HISTORY_FILE = "shield_history.log"

class BlueShieldStyles:
    """Clase para gestionar todo el diseño visual del sistema"""
    MAIN_THEME = """
        QMainWindow { background-color: #0d1117; }
        QToolBar { 
            background: #161b22; 
            border-bottom: 2px solid #3081f7; 
            padding: 8px; 
            spacing: 15px; 
        }
        QLineEdit { 
            background: #010409; 
            color: #58a6ff; 
            border: 1px solid #30363d; 
            border-radius: 12px; 
            padding: 8px 15px; 
            font-family: 'Consolas', monospace; 
        }
        QTabWidget::pane { border-top: 1px solid #30363d; background: #0d1117; }
        QTabBar::tab { 
            background: #1c2128; 
            color: #8b949e; 
            padding: 12px 25px; 
            border-right: 1px solid #0d1117; 
            min-width: 160px;
            font-weight: bold;
        }
        QTabBar::tab:selected { 
            background: #3081f7; 
            color: white; 
            border-bottom: 2px solid white;
        }
        QPushButton {
            background: #21262d;
            color: white;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px 15px;
            font-weight: bold;
        }
        QPushButton:hover { background: #3081f7; border-color: #58a6ff; }
        QTextEdit {
            background: #010409;
            color: #00ff88;
            font-family: 'Consolas';
            border: 1px solid #30363d;
        }
    """

# --- CLASES DE NAVEGACIÓN ---
class ShieldWebPage(QWebEnginePage):
    """Manejo avanzado de ventanas y permisos"""
    def __init__(self, window_parent):
        super().__init__()
        self.window_parent = window_parent

    def createWindow(self, _type):
        return self.window_parent.add_new_tab()

    def certificateError(self, error):
        # Aquí podrías añadir lógica de auditoría de SSL
        return super().certificateError(error)

# --- VENTANA DE AUTH ---
class AuthSystem(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield | Terminal Auth")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setStyleSheet("background-color: #0a0c10; color: white; border: 1px solid #3081f7;")
        
        # Logo y Título
        logo_label = QLabel("🛡️")
        logo_label.setStyleSheet("font-size: 80px; margin-top: 20px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("BLUE SHIELD OS")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #3081f7; letter-spacing: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Identificación de Operador...")
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Clave de Acceso...")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_layout = QHBoxLayout()
        login_btn = QPushButton("ACCEDER")
        login_btn.clicked.connect(self.handle_login)
        register_btn = QPushButton("REGISTRAR")
        register_btn.clicked.connect(self.handle_register)
        
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)

        layout.addWidget(logo_label)
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)

    def handle_login(self):
        # Lógica de sesión simple (puedes expandirla con JSON)
        if self.user_input.text() == "Enric" and self.pass_input.text() == "1234":
            self.accept()
        else:
            QMessageBox.critical(self, "Acceso Denegado", "Credenciales Inválidas.")

    def handle_register(self):
        QMessageBox.information(self, "Registro", "Función de registro de nuevo operador enviada al administrador.")

# --- VENTANA PRINCIPAL ---
class BlueShieldElite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield Elite | Terminal OS v3.0")
        self.setWindowIcon(QIcon("logo.jpg"))
        self.resize(1400, 900)

        # Contenedor Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Sistema de Pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Consola de Comandos (Ocultable)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFixedHeight(150)
        self.terminal.setPlaceholderText("Sistema Blue Shield inicializado...")
        self.terminal.hide()

        # Layout Final
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.terminal)

        self.init_toolbar()
        self.setStyleSheet(BlueShieldStyles.MAIN_THEME)

        # Pestañas de Inicio
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")
        self.add_new_tab(QUrl("https://iplogger.org"), "IP Logger")
        self.log_action("Sistema cargado satisfactoriamente.")

    def init_toolbar(self):
        self.toolbar = QToolBar("Navegación")
        self.addToolBar(self.toolbar)

        # Acciones
        back_btn = QAction("⬅️", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.toolbar.addAction(back_btn)

        reload_btn = QAction("🔄", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.toolbar.addAction(reload_btn)

        add_btn = QAction("➕", self)
        add_btn.triggered.connect(lambda: self.add_new_tab(QUrl("https://www.bing.com"), "Nueva Pestaña"))
        self.toolbar.addAction(add_btn)

        # Barra de búsqueda
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("¿Qué protocolo vamos a auditar hoy, Enric?")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        # Botón Consola
        term_btn = QAction("📟 CONSOLA", self)
        term_btn.triggered.connect(self.toggle_terminal)
        self.toolbar.addAction(term_btn)

    def add_new_tab(self, qurl=None, label="Cargando..."):
        browser = QWebEngineView()
        page = ShieldWebPage(self)
        browser.setPage(page)
        
        if qurl:
            browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Conexiones de señales
        browser.urlChanged.connect(lambda q, b=browser: self.update_url(q, b))
        browser.titleChanged.connect(lambda t, b=browser: self.update_title(t, b))
        browser.loadFinished.connect(lambda _, b=browser: self.log_action(f"Cargado: {b.url().toString()}"))
        
        return page

    def log_action(self, message):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.terminal.append(f"[{time_str}] > {message}")

    def toggle_terminal(self):
        if self.terminal.isHidden():
            self.terminal.show()
        else:
            self.terminal.hide()

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "": q.setScheme("https")
        self.tabs.currentWidget().setUrl(q)

    def update_url(self, q, browser):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())

    def update_title(self, title, browser):
        i = self.tabs.indexOf(browser)
        if i != -1: self.tabs.setTabText(i, title[:20])

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

# --- LANZADOR ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Blue Shield Elite")
    
    auth = AuthSystem()
    if auth.exec() == QDialog.DialogCode.Accepted:
        window = BlueShieldElite()
        window.show()
        sys.exit(app.exec())
