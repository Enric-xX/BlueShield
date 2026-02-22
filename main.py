#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blue Shield Elite v2.6 – Navegador de ciberseguridad con Chromium embebido
"""

import sys
import os
import json
import socket
import hashlib
import secrets
from pathlib import Path
from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit,
    QMessageBox, QInputDialog, QAction
)
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

# ────────────────────────────────────────────────
#               CONFIGURACIÓN GLOBAL
# ────────────────────────────────────────────────

DB_PATH = Path("shield_db.json")
DEFAULT_START_PAGE = "https://search.brave.com"
APP_NAME = "Blue Shield Elite"
APP_VERSION = "2.6"

# Fix común para pantallas negras / blancas en algunos drivers
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-software-rasterizer"

# ────────────────────────────────────────────────
#                   AUTENTICACIÓN
# ────────────────────────────────────────────────

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        n=16384, r=8, p=1, dklen=32
    ).hex()
    return hashed, salt


class AuthManager:
    @staticmethod
    def register(username: str, password: str):
        hashed, salt = hash_password(password)
        DB_PATH.write_text(json.dumps({
            "username": username.strip(),
            "password_hash": hashed,
            "salt": salt
        }, indent=2, ensure_ascii=False))

    @staticmethod
    def verify(password: str) -> bool:
        if not DB_PATH.exists():
            return False
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        hashed_input, _ = hash_password(password, data["salt"])
        return hashed_input == data["password_hash"]

    @staticmethod
    def get_username() -> str:
        if DB_PATH.exists():
            return json.loads(DB_PATH.read_text(encoding="utf-8")).get("username", "Usuario")
        return "Usuario"


# ────────────────────────────────────────────────
#                   VENTANA PRINCIPAL
# ────────────────────────────────────────────────

class BlueShieldBrowser(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Perfil aislado por pestaña (más privacidad)
        self.page().profile().setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies
        )
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)

    def createWindow(self, _type):
        # Intercepta todos los links que intenten abrir nueva ventana/pestaña
        return self.window().create_new_tab(QUrl(), "Nueva pestaña")


class BlueShieldWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1400, 900)
        self.showMaximized()

        self.auth_manager = AuthManager()
        if not self.authenticate():
            sys.exit(0)

        self.init_ui()
        self.create_shortcuts()

    def authenticate(self):
        if not DB_PATH.exists():
            user, ok1 = QInputDialog.getText(self, "Registro", "Crea tu nombre de usuario:")
            if not ok1 or not user.strip():
                return False

            pw, ok2 = QInputDialog.getText(
                self, "Registro", "Crea tu Clave Maestra:", QLineEdit.EchoMode.Password
            )
            if not ok2 or not pw:
                return False

            self.auth_manager.register(user, pw)
            QMessageBox.information(self, "Éxito", "Usuario creado.\nReinicia la aplicación.")
            return False

        # Login
        pw, ok = QInputDialog.getText(
            self, "Autenticación", f"Bienvenido {self.auth_manager.get_username()}\nClave Maestra:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return False

        if self.auth_manager.verify(pw):
            return True

        QMessageBox.critical(self, "Acceso denegado", "Clave incorrecta.")
        return False

    def init_ui(self):
        # ── Pestañas ────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # ── Barra de navegación ─────────────────────
        toolbar = QToolBar("Navegación")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Acciones
        home_action = QAction("🏠 Inicio", self)
        home_action.triggered.connect(self.go_home)
        toolbar.addAction(home_action)

        new_tab_action = QAction("➕ Nueva pestaña", self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(lambda: self.create_new_tab())
        toolbar.addAction(new_tab_action)

        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Protocolo a auditar... (ej: https://target.com)")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setClearButtonEnabled(True)
        toolbar.addWidget(self.url_bar)

        stats_action = QAction("📟 RED", self)
        stats_action.triggered.connect(self.show_network_info)
        toolbar.addAction(stats_action)

        self.apply_dark_theme()

        # Primera pestaña
        self.create_new_tab(QUrl(DEFAULT_START_PAGE), "Inicio")

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0c10;
            }
            QToolBar {
                background: #161b22;
                border-bottom: 2px solid #1e6feb;
                padding: 6px;
                spacing: 8px;
            }
            QLineEdit {
                background: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 6px 10px;
                selection-background-color: #1e6feb;
            }
            QTabWidget::pane {
                border: 1px solid #30363d;
                background: #0d1117;
            }
            QTabBar::tab {
                background: #161b22;
                color: #8b949e;
                padding: 10px 24px;
                margin-right: 2px;
                border: 1px solid #30363d;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #1e6feb;
                color: white;
                font-weight: bold;
            }
            QTabBar::close-button {
                image: none;
                subcontrol-position: right;
            }
        """)

    def create_new_tab(self, url: QUrl = None, title: str = "Nueva pestaña"):
        if url is None or not url.isValid():
            url = QUrl(DEFAULT_START_PAGE)

        browser = BlueShieldBrowser(self)
        browser.setUrl(url)

        idx = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(idx)

        # Actualizaciones dinámicas
        browser.urlChanged.connect(lambda qurl: self.on_url_changed(qurl, browser))
        browser.titleChanged.connect(lambda title: self.tabs.setTabText(idx, (title or "Sin título")[:40]))
        browser.iconChanged.connect(lambda icon: self.tabs.setTabIcon(idx, icon))

        return browser

    def on_url_changed(self, qurl: QUrl, browser):
        if self.tabs.currentWidget() == browser:
            self.url_bar.setText(qurl.toString())

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return

        if not text.startswith(("http://", "https://")):
            text = "https://" + text

        url = QUrl(text)
        if url.isValid():
            self.tabs.currentWidget().setUrl(url)
        else:
            QMessageBox.warning(self, "URL inválida", "La dirección no parece correcta.")

    def go_home(self):
        self.create_new_tab(QUrl(DEFAULT_START_PAGE), "Inicio")

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def show_network_info(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            pub_ip = "No disponible"
            import requests
            pub_ip = requests.get("https://api.ipify.org", timeout=4).text
        except Exception as e:
            pub_ip = f"Error: {str(e)}"

        username = self.auth_manager.get_username()
        info = f"Usuario: {username}\nHostname: {hostname}\nIP local: {local_ip}\nIP pública: {pub_ip}"
        QMessageBox.information(self, "Estado de Red", info)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    window = BlueShieldWindow()
    window.show()
    sys.exit(app.exec())
