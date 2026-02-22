# Añade esto dentro de la clase de tu navegador
self.setStyleSheet("""
    QMainWindow {
        background-color: #0b0e14;
    }
    QToolBar {
        background-color: #161b22;
        border-bottom: 2px solid #3081f7; /* La línea azul del escudo */
        padding: 5px;
        spacing: 10px;
    }
    QLineEdit {
        background-color: #0d1117;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 15px;
        padding: 5px 15px;
        font-family: 'Segoe UI';
    }
    QPushButton {
        background-color: #1f6feb;
        color: white;
        border-radius: 8px;
        padding: 5px 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #388bfd;
    }
""")
