##1360276491457922376189
##4920288647699760539556
##9316273982896818412529
##2197126032733305545493
##3503819429555534003883
import subprocess
import sys
import json
import os
import time
import threading
import tempfile
from multiprocessing import Queue
from ctypes import windll

import numpy as np
import cv2
import win32api
import bettercam
from colorama import init, Fore, Back, Style

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def instalar_paquete(paquete):
    print(f"Instalando {paquete}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

def chequear_e_instalar(paquetes):
    import importlib
    for paquete, modulo in paquetes.items():
        try:
            importlib.import_module(modulo)
        except ImportError:
            instalar_paquete(paquete)

paquetes_requeridos = {
    "colorama": "colorama",
    "numpy": "numpy",
    "opencv-python": "cv2",
    "pywin32": "win32api",
    "bettercam": "bettercam",
}

chequear_e_instalar(paquetes_requeridos)


CONFIG_FILE = "config.json"

KEY_MAP = {
    "ALT": 0x12,
    "SHIFT": 0x10,
    "CTRL": 0x11,
    "TAB": 0x09,
    "M1": 0x01,
    "M2": 0x02,
    "M3": 0x04,
    "M4": 0x05,
    "M5": 0x06,
}

COLOR_HSV_MAP = {
    "ROJO": [[0, 200, 150], [15, 255, 255]],
    "AMARILLO": [[20, 100, 100], [40, 255, 255]],
    "MORADO": [[130, 150, 100], [160, 255, 255]],
}


def cargar_config():
    if not os.path.isfile(CONFIG_FILE):
        return {
            "fov": 5,
            "keybind_type": "raton",
            "keybind": "M5",
            "color": "AMARILLO",
            "shooting_rate": 10,
            "fps": 120
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def guardar_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def input_int(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Introduce un valor entre {min_val} y {max_val}.")
        except ValueError:
            print("Por favor, introduce un número válido.")

def input_choice(prompt, choices):
    choices_str = ", ".join(choices)
    while True:
        val = input(f"{prompt} ({choices_str}): ").strip().upper()
        if val in choices:
            return val
        else:
            print("Opción no válida.")


class StarBot(threading.Thread):
    def __init__(self, queue, keybind_type, keybind, fov, color, shooting_rate, fps):
        super().__init__()
        self.queue = queue
        self.keybind = KEY_MAP.get(keybind)
        self.base_fov = fov
        self.hsv_ranges = [
            (np.array(COLOR_HSV_MAP[color][0], dtype=np.uint8),
             np.array(COLOR_HSV_MAP[color][1], dtype=np.uint8))
        ]
        self.shooting_rate = shooting_rate
        self.fps = fps
        self.camera = None
        self.last_width = 0
        self.last_height = 0
        self.check_region = None
        self._stop_event = threading.Event()

    def update_resolution_and_camera(self):
        user32 = windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        if width != self.last_width or height != self.last_height or self.camera is None:
            if self.camera:
                try:
                    self.camera.stop()
                except:
                    pass
                del self.camera
                time.sleep(0.3)

            self.last_width = width
            self.last_height = height
            scale = ((width / 1920) + (height / 1080)) / 2
            scaled_fov = int(self.base_fov * scale)
            cx, cy = width // 2, height // 2
            self.check_region = (cx - scaled_fov, cy - scaled_fov, cx + scaled_fov, cy + scaled_fov)

            self.camera = bettercam.create(output_idx=0, region=self.check_region)
            self.camera.start(target_fps=self.fps)

    def Color(self):
        if not self.camera:
            return False
        frame = self.camera.get_latest_frame()
        if frame is None:
            return False
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        for cmin, cmax in self.hsv_ranges:
            mask = cv2.inRange(hsv, cmin, cmax)
            if np.any(mask):
                return True
        return False

    def run(self):
        while not self._stop_event.is_set():
            self.update_resolution_and_camera()
            if self.camera and self.keybind:
                if win32api.GetAsyncKeyState(self.keybind) < 0 and self.Color():
                    self.queue.put("Shoot")
                    time.sleep(self.shooting_rate / 1000)
            time.sleep(0.001)

    def stop(self):
        self._stop_event.set()
        if self.camera:
            try:
                self.camera.stop()
            except:
                pass


def bypass(queue, stop_event):
    trigger_file = os.path.join(tempfile.gettempdir(), "star_8k3jz4n0.txt")
    while not stop_event.is_set():
        try:
            signal = queue.get(timeout=0.1)
            if signal == "Shoot":
                try:
                    with open(trigger_file, 'w') as f:
                        f.write("shoot")
                except:
                    pass
        except:
            pass


def editar_config():
    config = cargar_config()

    print("\n--- EDITAR CONFIGURACIÓN ---")

    fov = input_int("Configurar FOV (1-10): ", 1, 10)

    print("\nSelecciona tipo de keybind:")
    print("1 - teclado")
    print("2 - raton")
    while True:
        keybind_type_input = input("Opción: ").strip()
        if keybind_type_input == "1":
            keybind_type = "teclado"
            keybind_choices = ["ALT", "SHIFT", "CTRL", "TAB"]
            break
        elif keybind_type_input == "2":
            keybind_type = "raton"
            keybind_choices = ["M1", "M2", "M3", "M4", "M5"]
            break
        else:
            print("Opción no válida, elige 1 o 2.")

    keybind = input_choice("Introduce keybind", keybind_choices)

    color = input_choice("Selecciona color", COLOR_HSV_MAP.keys())

    shooting_rate = input_int("Introduce shooting rate (ms): ", 1, 10000)

    fps = input_int("Introduce FPS: ", 1, 1000)

    print("\n¿Desea guardar los datos? (s/n): ", end="")
    save = input().strip().lower()
    if save == "s":
        new_config = {
            "fov": fov,
            "keybind_type": keybind_type,
            "keybind": keybind,
            "color": color,
            "shooting_rate": shooting_rate,
            "fps": fps
        }
        guardar_config(new_config)
        print("Configuración guardada.")
    else:
        print("No se guardaron los cambios.")


def init():
    from colorama import init as colorama_init
    colorama_init(autoreset=True)


def main_menu():
    init()
    StarBot_thread = None
    queue = Queue()
    bypass_stop_event = threading.Event()
    bypass_thread = threading.Thread(target=bypass, args=(queue, bypass_stop_event), daemon=True)
    bypass_thread.start()

    while True:
        clear_screen()

        print("\n⭐ STARHOOK v3 by @uidnull.\n")
        print("1 LOAD STARHOOK")
        print("2 EDITAR CONFIG")
        print("3 STOP STARHOOK")
        print("4 SALIR\n")

        option = input("Elige una opción: ").strip()

        if option == "1":
            if StarBot_thread and StarBot_thread.is_alive():
                print(Fore.YELLOW + "STARHOOK ya se está ejecutando." + Style.RESET_ALL)
                input("\nPresiona Enter para volver al menú...")
                continue

            config = cargar_config()
            StarBot_thread = StarBot(
                queue,
                config["keybind_type"],
                config["keybind"],
                config["fov"],
                config["color"],
                config["shooting_rate"],
                config["fps"]
            )
            StarBot_thread.start()
            print(Fore.GREEN + "STARHOOK cargado y ejecutándose." + Style.RESET_ALL)
            input("\nPresiona Enter para volver al menú...")

        elif option == "2":
            if StarBot_thread and StarBot_thread.is_alive():
                print(Fore.YELLOW + "Primero detén STARHOOK para editar la configuración." + Style.RESET_ALL)
                input("\nPresiona Enter para volver al menú...")
            else:
                editar_config()
                input("\nPresiona Enter para volver al menú...")

        elif option == "3":
            if StarBot_thread and StarBot_thread.is_alive():
                print("Deteniendo STARHOOK...")
                StarBot_thread.stop()
                StarBot_thread.join()
                StarBot_thread = None
                print(Fore.RED + "STARHOOK detenido." + Style.RESET_ALL)
                input("\nPresiona Enter para volver al menú...")
            else:
                print(Fore.YELLOW + "STARHOOK no se está ejecutando." + Style.RESET_ALL)
                input("\nPresiona Enter para volver al menú...")

        elif option == "4":
            print("Saliendo...")
            if StarBot_thread and StarBot_thread.is_alive():
                StarBot_thread.stop()
                StarBot_thread.join()
            bypass_stop_event.set()
            bypass_thread.join()
            break

        else:
            print("Opción no válida.")
            input("\nPresiona Enter para volver al menú...")

if __name__ == "__main__":
    main_menu()
##7751050796369267317802
##8575556040342184108476
##8916264190292508457033
##3707139616610109917920
##2183885071417203326979
