import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import QIcon, QAction

class BlueShieldPython(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield Elite Edition")
        
        # El motor del navegador
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://gemini.google.com"))
        self.setCentralWidget(self.browser)

        # Estética Dark
        self.setStyleSheet("QMainWindow { background-color: #0d1117; } QToolBar { background: #161b22; border-bottom: 1px solid #3081f7; }")

        # Barra de navegación
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        # Función para añadir botones de webs rápido
        def add_web(name, url):
            act = QAction(name, self)
            act.triggered.connect(lambda: self.browser.setUrl(QUrl(url)))
            nav_bar.addAction(act)

        # Añadiendo tus webs al menú superior
        add_web("Gemini", "https://gemini.google.com")
        add_web("Drive", "https://drive.google.com")
        add_web("GitHub", "https://github.com")
        add_web("JSFiddle", "https://jsfiddle.net")
        add_web("IPLogger", "https://iplogger.org/es/")

        # Barra de URL real
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        self.showMaximized()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"): url = "https://" + url
        self.browser.setUrl(QUrl(url))

app = QApplication(sys.argv)
window = BlueShieldPython()
app.exec()
