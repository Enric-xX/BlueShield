#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blue Shield Elite v2.6 – Navegador de ciberseguridad con Chromium embebido
Creado para uso local con autenticación cifrada
"""

import sys
import os
import socket
import json
from pathlib import Path
from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit,
    QMessageBox, QInputDialog, QAction
)
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtGui import QKeySequence, QShortcut

# ── Importamos nuestra lógica de autenticación ──
from auth import AuthManager

# ────────────────────────────────────────────────
#               CONFIGURACIÓN
# ────────────────────────────────────────────────

DB_PATH = Path("shield_db.enc")
DEFAULT_START_PAGE = "https://search.brave.com"
APP_NAME = "Blue Shield Elite"
APP_VERSION = "2.6"

# Fix para problemas gráficos en algunos sistemas
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-software-rasterizer"


class SecureBrowser(QWebEngineView):
    """Vista de navegador que fuerza apertura interna de enlaces"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Perfil sin cookies persistentes (más privacidad)
        self.page().profile().setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies
        )
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

    def createWindow(self, _type):
        return self.window().create_new_tab(QUrl(), "Nueva pestaña")


class BlueShieldWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1440, 900)
        self.showMaximized()

        self.current_username = "Usuario"
        if not self.authenticate():
            sys.exit(0)

        self.init_ui()
        self.create_shortcuts()

    def authenticate(self) -> bool:
        auth = AuthManager()

        if not auth.exists():
            # ── REGISTRO ───────────────────────────────────
            user, ok1 = QInputDialog.getText(self, 'Registro', 'Crea tu nombre de usuario:')
            if not ok1 or not user.strip():
                QMessageBox.warning(self, "Cancelado", "Registro cancelado.")
                return False

            pw, ok2 = QInputDialog.getText(
                self, 'Registro', 'Crea tu Clave Maestra (mín 8 caracteres):',
                QLineEdit.EchoMode.Password
            )
            if not ok2 or len(pw) < 8:
                QMessageBox.warning(self, "Error", "Clave demasiado corta o cancelada.")
                return False

            pw_confirm, ok3 = QInputDialog.getText(
                self, 'Confirmar', 'Repite tu Clave Maestra:',
                QLineEdit.EchoMode.Password
            )
            if not ok3 or pw != pw_confirm:
                QMessageBox.critical(self, "Error", "Las claves no coinciden.")
                return False

            if auth.register(user, pw):
                QMessageBox.information(self, "Éxito",
                    f"Usuario '{user}' registrado correctamente.\n\n"
                    "Reinicia la aplicación para iniciar sesión.")
                return False
            else:
                QMessageBox.critical(self, "Error", "No se pudo crear el registro.")
                return False

        # ── LOGIN ──────────────────────────────────────
        pw, ok = QInputDialog.getText(
            self, f"{APP_NAME}", f"Bienvenido\nIntroduce tu Clave Maestra:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return False

        success, username = auth.login(pw)
        if success:
            self.current_username = username
            return True
        else:
            QMessageBox.critical(self, "Acceso denegado", "Clave incorrecta.")
            return False

    def init_ui(self):
        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar
        toolbar = QToolBar("Navegación")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Acciones
        home_act = QAction("🏠 Inicio", self)
        home_act.triggered.connect(self.go_home)
        toolbar.addAction(home_act)

        new_act = QAction("➕ Nueva pestaña", self)
        new_act.setShortcut(QKeySequence("Ctrl+T"))
        new_act.triggered.connect(lambda: self.create_new_tab())
        toolbar.addAction(new_act)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Protocolo a auditar... (ej: https://example.com)")
        self.url_bar.returnPressed.connect(self.navigate)
        self.url_bar.setClearButtonEnabled(True)
        toolbar.addWidget(self.url_bar)

        stats_act = QAction("📟 RED", self)
        stats_act.triggered.connect(self.show_network_info)
        toolbar.addAction(stats_act)

        self.apply_theme()

        # Pestaña inicial
        self.create_new_tab(QUrl(DEFAULT_START_PAGE), "Inicio")

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #0a0c10; }
            QToolBar {
                background: #161b22;
                border-bottom: 2px solid #1e6feb;
                padding: 6px;
                spacing: 10px;
            }
            QLineEdit {
                background: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QTabWidget::pane {
                border: 1px solid #30363d;
                background: #0d1117;
            }
            QTabBar::tab {
                background: #161b22;
                color: #8b949e;
                padding: 10px 22px;
                border: 1px solid #30363d;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #1e6feb;
                color: white;
                font-weight: bold;
            }
        """)

    def create_new_tab(self, url: QUrl = None, title: str = "Nueva"):
        if url is None or not url.isValid():
            url = QUrl(DEFAULT_START_PAGE)

        browser = SecureBrowser(self)
        browser.setUrl(url)

        idx = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(idx)

        browser.urlChanged.connect(lambda q: self.on_url_changed(q, browser))
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(idx, (t or "Sin título")[:35]))

        return browser

    def on_url_changed(self, qurl: QUrl, browser):
        if self.tabs.currentWidget() == browser:
            self.url_bar.setText(qurl.toString())

    def navigate(self):
        text = self.url_bar.text().strip()
        if not text:
            return

        if not text.startswith(("http://", "https://")):
            text = "https://" + text

        url = QUrl(text)
        if url.isValid():
            self.tabs.currentWidget().setUrl(url)
        else:
            QMessageBox.warning(self, "URL inválida", "Dirección no válida.")

    def go_home(self):
        self.create_new_tab(QUrl(DEFAULT_START_PAGE), "Inicio")

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def show_network_info(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            import requests
            pub_ip = requests.get("https://api.ipify.org", timeout=5).text
        except Exception as e:
            pub_ip = f"Error: {str(e)[:60]}"

        info = (
            f"Usuario: {self.current_username}\n"
            f"Hostname: {hostname}\n"
            f"IP local: {local_ip}\n"
            f"IP pública: {pub_ip}"
        )
        QMessageBox.information(self, "Información de Red", info)

    def create_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.create_new_tab())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    window = BlueShieldWindow()
    window.show()
    sys.exit(app.exec())
