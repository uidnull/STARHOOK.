import os
import sys
import json
import time
import threading
import subprocess
import tempfile
from multiprocessing import Queue
from ctypes import windll

import numpy as np
import cv2
import win32api
import bettercam
from colorama import init as colorama_init, Fore, Style

# --- Auto-installation check for pypresence ---
try:
    from pypresence import Presence
except ImportError:
    print("El módulo 'pypresence' no se encontró. Intentando instalarlo...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypresence"])
        from pypresence import Presence
        print("Módulo 'pypresence' instalado exitosamente.")
    except Exception as e:
        print(f"ERROR: No se pudo instalar 'pypresence' automáticamente. Por favor, instálalo manualmente ejecutando:")
        print(f"pip install pypresence")
        print(f"Detalle del error: {e}")
        input("Presiona Enter para cerrar...")
        sys.exit(1)  # Exit the script if installation fails
# --- End of auto-installation check ---

# Otros paquetes requeridos e instalación automática
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

# Constantes
CONFIG_FILE = "config.json"
DISCORD_CLIENT_ID = "1402079582257021009"

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

# Funciones auxiliares
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: El archivo '{CONFIG_FILE}' no es un JSON válido. Usando valores predeterminados.")
        return {
            "fov": 5,
            "keybind_type": "raton",
            "keybind": "M5",
            "color": "AMARILLO",
            "shooting_rate": 10,
            "fps": 120
        }
    except Exception as e:
        print(f"Error al cargar '{CONFIG_FILE}': {e}. Usando valores predeterminados.")
        return {
            "fov": 5,
            "keybind_type": "raton",
            "keybind": "M5",
            "color": "AMARILLO",
            "shooting_rate": 10,
            "fps": 120
        }

def guardar_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
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

# Clase Discord RPC
class DiscordRPC(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.rpc = None
        self.connected = False
        self.running = True

    def run(self):
        try:
            self.rpc = Presence(DISCORD_CLIENT_ID)
            self.rpc.connect()
            self.connected = True
            self.actualizar_estado()
            # Mantener el hilo vivo para poder actualizar estado o desconectar
            while self.running:
                time.sleep(15)  # Actualización periódica opcional
        except Exception as e:
            print(f"Error en Discord RPC: {e}")
            self.connected = False

    def actualizar_estado(self):
        if not self.connected:
            return
        config = cargar_config()
        keybind = config.get("keybind", "N/A")
        fov = config.get("fov", "N/A")
        details = f"KEY [{keybind}] + FOV [{fov}]"
        try:
            self.rpc.update(
                state="VALORANT",
                details=details,
                start=int(time.time()),
                large_image="1",
                large_text="StarHook v3",
                buttons=[{"label": "Discord", "url": "https://discord.gg/EVXfv8VNDP"}],
            )
        except Exception as e:
            print(f"Error actualizando estado Discord RPC: {e}")

    def close(self):
        self.running = False
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except Exception as e:
                print(f"Error al cerrar conexión Discord RPC: {e}")

# Clase principal StarBot
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

# Función bypass para escribir archivo de disparo
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

# Función para editar configuración
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

# Inicialización colorama
def init():
    colorama_init(autoreset=True)

# Menú principal
def main_menu():
    init()
    StarBot_thread = None
    queue = Queue()
    bypass_stop_event = threading.Event()
    bypass_thread = threading.Thread(target=bypass, args=(queue, bypass_stop_event), daemon=True)
    bypass_thread.start()

    # Iniciar RPC Discord en hilo aparte
    discord_rpc = DiscordRPC()
    discord_rpc.start()

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
            # Actualizar estado Discord con nueva configuración
            discord_rpc.actualizar_estado()
            print(Fore.GREEN + "STARHOOK cargado y ejecutándose." + Style.RESET_ALL)
            input("\nPresiona Enter para volver al menú...")

        elif option == "2":
            if StarBot_thread and StarBot_thread.is_alive():
                print(Fore.YELLOW + "Primero detén STARHOOK para editar la configuración." + Style.RESET_ALL)
                input("\nPresiona Enter para volver al menú...")
            else:
                editar_config()
                # Actualizar estado Discord tras editar config
                discord_rpc.actualizar_estado()
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
            discord_rpc.close()
            break

        else:
            print("Opción no válida.")
            input("\nPresiona Enter para volver al menú...")

if __name__ == "__main__":
    main_menu()
