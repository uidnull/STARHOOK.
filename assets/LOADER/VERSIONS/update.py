import sys
import threading
import urllib.request
import json
import tempfile
import ctypes
import hashlib
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

# URLs base
KEYS_URL = "https://raw.githubusercontent.com/uidnull/STARHOOK./main/assets/LOADER/KEYS/valid.json"
LOGO_URL = "https://raw.githubusercontent.com/uidnull/STARHOOK./main/starhook.png"

# URLs de versionado
CURRENT_VERSION_URL = "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/assets/LOADER/VERSIONS/current.py"
UPDATE_VERSION_URL = "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/assets/LOADER/VERSIONS/update.py"

ICON_URL = "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/starhook.ico"

# Juegos y scripts asociados
GAMES = [
    {
        "name": "Valorant",
        "description": "COLOR BOT",
        "image": "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/assets/v_s.png",
        "script_url": "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/assets/languages/spanish/valorant_es.py"
    },
    {
        "name": "THE FINALS",
        "description": "COLOR BOT",
        "image": "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/assets/tf_s.png",
        "script_url": "https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/assets/languages/spanish/thefinals_es.py"
    }
]

def get_hash_and_length(url):
    data = urllib.request.urlopen(url).read()
    h = hashlib.md5(data).hexdigest()
    length = len(data)
    return h, length

def check_version():
    try:
        h_current, len_current = get_hash_and_length(CURRENT_VERSION_URL)
        h_update, len_update = get_hash_and_length(UPDATE_VERSION_URL)
        print(f"Current file: length={len_current}, md5={h_current}")
        print(f"Update file:  length={len_update}, md5={h_update}")
        if h_current != h_update:
            QMessageBox.critical(None, "ERROR", "ACTUALIZA EL LOADER")
            sys.exit(0)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"No se pudo verificar la versión:\n{e}")
        sys.exit(1)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Descargar icono temporalmente y asignar
        try:
            data = urllib.request.urlopen(ICON_URL).read()
            tmp_icon = tempfile.NamedTemporaryFile(delete=False, suffix=".ico")
            tmp_icon.write(data)
            tmp_icon.close()
            self.setWindowIcon(QIcon(tmp_icon.name))
            self._temp_icon_path = tmp_icon.name
        except Exception as e:
            print(f"Error cargando icono: {e}")

        self.setWindowTitle("STARHOOK LOADER")
        self.setFixedSize(500, 400)
        self.layout = QVBoxLayout(self)
        self.init_login_ui()

    def closeEvent(self, event):
        # Borra el archivo temporal del icono al cerrar
        try:
            if hasattr(self, '_temp_icon_path') and os.path.exists(self._temp_icon_path):
                os.remove(self._temp_icon_path)
        except Exception:
            pass
        super().closeEvent(event)

    def init_login_ui(self):
        self.clear_layout()

        pixmap = QPixmap()
        try:
            data = urllib.request.urlopen(LOGO_URL).read()
            pixmap.loadFromData(data)
            pixmap = pixmap.scaled(150, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            print(f"Error cargando logo: {e}")
        lbl = QLabel()
        lbl.setPixmap(pixmap)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl)

        title = QLabel("STARHOOK")
        title.setStyleSheet("font-size:20px; font-weight:bold; color:white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Ingresa tu key")
        self.key_input.setFixedWidth(280)
        self.layout.addWidget(self.key_input, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Login")
        btn.setFixedWidth(100)
        btn.clicked.connect(self.check_key)
        self.layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            QWidget{background:#111; color:white;}
            QLineEdit{padding:6px; border-radius:5px; background:#222; border:1px solid #555;}
            QPushButton{padding:6px; border-radius:5px; background:#333;} QPushButton:hover{background:#555;}
        """)

    def clear_layout(self):
        while self.layout.count():
            w = self.layout.takeAt(0).widget()
            if w:
                w.deleteLater()

    def check_key(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Aviso", "Por favor ingresa una key.")
            return
        try:
            data = urllib.request.urlopen(KEYS_URL).read()
            keys = json.loads(data.decode()).get("valid_keys", [])
            if key in keys:
                self.show_games_panel()
            else:
                QMessageBox.critical(self, "Error", "Key inválida.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo verificar la key:\n{e}")

    def show_games_panel(self):
        self.clear_layout()
        self.setFixedSize(700, 500)

        title = QLabel("SCRIPTS DISPONIBLES")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        for game in GAMES:
            vbox.addWidget(self.create_card(game))
        self.layout.addWidget(scroll)

    def create_card(self, game):
        frame = QFrame()
        frame.setFixedHeight(120)
        frame.setStyleSheet("QFrame{border:2px solid #444; border-radius:10px; background:#222;}")

        h = QHBoxLayout(frame)
        pix = QPixmap()
        try:
            data = urllib.request.urlopen(game["image"]).read()
            pix.loadFromData(data)
            pix = pix.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            print(f"Error cargando imagen: {e}")
        img = QLabel()
        img.setPixmap(pix)
        img.setFixedSize(100, 100)
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(img)

        txt = QVBoxLayout()
        name = QLabel(game["name"])
        name.setStyleSheet("font-size:16px; font-weight:bold; border:none;")
        desc = QLabel(game["description"])
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size:12px; border:none;")
        txt.addWidget(name)
        txt.addWidget(desc)
        h.addLayout(txt)

        btn = QPushButton("Launch")
        btn.setFixedWidth(80)
        btn.clicked.connect(lambda _, url=game["script_url"]: threading.Thread(target=self.run_script_as_admin, args=(url,), daemon=True).start())
        h.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        return frame

    def run_script_as_admin(self, script_url):
        try:
            code = urllib.request.urlopen(script_url).read().decode("utf-8")
            tmp_py = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
            tmp_py.write(code)
            tmp_py.close()
            cmd = f'python "{tmp_py.name}"'
            self.run_as_admin(cmd)
        except Exception as e:
            print(f"Error ejecutando script desde {script_url}: {e}")

    def run_as_admin(self, command):
        params = f'/c {command}'
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "cmd.exe",
            params,
            None,
            1
        )
        if ret <= 32:
            print(f"Error al ejecutar como admin. Código: {ret}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    check_version()  # Si falla, alerta + cierre aquí
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
