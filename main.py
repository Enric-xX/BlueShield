import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *

class BlueShield(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Shield - Elite Navigator")
        self.setWindowIcon(QIcon("logo.jpg"))
        
        # Sistema de Pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        
        self.setCentralWidget(self.tabs)
        
        # Estilo Global (Dark Blue Elite)
        self.setStyleSheet("""
            QMainWindow { background-color: #0a0c10; }
            QTabWidget::pane { border-top: 2px solid #00a2ff; }
            QTabBar::tab { background: #11141b; color: #8b949e; padding: 10px; border-right: 1px solid #30363d; }
            QTabBar::tab:selected { background: #00a2ff; color: white; }
            QLineEdit { background: #010409; color: #58a6ff; border: 1px solid #30363d; padding: 8px; border-radius: 15px; }
        """)

        # Barra de herramientas
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        self.add_new_tab(QUrl("https://search.brave.com"), "Inicio")
        self.showMaximized()

    def add_new_tab(self, qurl=None, label="Nueva Pestaña"):
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Actualizar URL al navegar
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url(qurl, browser))

    def tab_open_doubleclick(self, i):
        if i == -1: self.add_new_tab(QUrl("https://search.brave.com"))

    def close_current_tab(self, i):
        if self.tabs.count() > 1: self.tabs.removeTab(i)

    def update_url(self, q, browser=None):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "": q.setScheme("https")
        self.tabs.currentWidget().setUrl(q)

app = QApplication(sys.argv)
window = BlueShield()
app.exec()
