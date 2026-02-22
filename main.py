import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import QWebEnginePage

class WebEnginePage(QWebEnginePage):
    # Esta clase permite que los enlaces que piden "ventana nueva" 
    # se abran como pestañas dentro de nuestro propio Blue Shield
    def createWindow(self, _type):
        return window.add_new_tab()

class BlueShieldElite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield Elite | Multi-Tasking OS")
        self.resize(1300, 900)

        # Widget de Pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar Profesional
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Botones de navegación
        back_btn = QAction("⬅️", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        toolbar.addAction(back_btn)

        fwd_btn = QAction("➡️", self)
        fwd_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        toolbar.addAction(fwd_btn)

        reload_btn = QAction("🔄", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        toolbar.addAction(reload_btn)

        add_tab_btn = QAction("➕", self)
        add_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl("https://grok.com"), "Nueva Pestaña"))
        toolbar.addAction(add_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setPlaceholderText("Introduce URL o comando de búsqueda...")
        toolbar.addWidget(self.url_bar)

        # Estilo Dark Premium
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QToolBar { background: #161b22; padding: 8px; border-bottom: 2px solid #3081f7; spacing: 10px; }
            QLineEdit { background: #010409; color: #58a6ff; border: 1px solid #30363d; border-radius: 12px; padding: 6px 12px; font-family: 'Consolas'; }
            QTabWidget::pane { border-top: 1px solid #30363d; }
            QTabBar::tab { background: #1c2128; color: #8b949e; padding: 12px 25px; border-right: 1px solid #0d1117; min-width: 150px; }
            QTabBar::tab:selected { background: #3081f7; color: white; font-weight: bold; }
            QTabBar::close-button { image: url(close_icon.png); subcontrol-position: right; }
        """)

        # Cargar sesión inicial simultánea
        self.add_new_tab(QUrl("https://grok.com"), "Grok AI")
        self.add_new_tab(QUrl("https://github.com"), "GitHub")
        
    def add_new_tab(self, qurl=None, label="Nueva Pestaña"):
        browser = QWebEngineView()
        # Usamos nuestra clase personalizada para capturar ventanas nuevas
        page = WebEnginePage(browser)
        browser.setPage(page)
        
        if qurl: browser.setUrl(qurl)
        
        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)
        
        # Actualizar barra de URL y título de pestaña
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url(qurl, browser))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
        
        return page

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1: self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)

    def update_url(self, q, browser):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())

    def navigate_to_url(self):
        url = QUrl(self.url_bar.text())
        if url.scheme() == "": url.setScheme("https")
        self.tabs.currentWidget().setUrl(url)

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

app = QApplication(sys.argv)
window = BlueShieldElite()
window.show()
sys.exit(app.exec())
