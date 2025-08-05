
import os
import json
import time
import sys

# --- Auto-installation check for pypresence ---
try:
    from pypresence import Presence
except ImportError:
    print("El módulo 'pypresence' no se encontró. Intentando instalarlo...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypresence"])
        from pypresence import Presence
        print("Módulo 'pypresence' instalado exitosamente.")
    except Exception as e:
        print(f"ERROR: No se pudo instalar 'pypresence' automáticamente. Por favor, instálalo manualmente ejecutando:")
        print(f"pip install pypresence")
        print(f"Detalle del error: {e}")
        input("Presiona Enter para cerrar...")
        sys.exit(1) # Exit the script if installation fails
# --- End of auto-installation check ---

DISCORD_CLIENT_ID = "1402079582257021009"
CONFIG_FILE = "config.json"

def cargar_config():
    """Carga la configuración desde config.json o devuelve valores predeterminados."""
    if not os.path.isfile(CONFIG_FILE):
        print(f"Advertencia: No se encontró '{CONFIG_FILE}'. Usando valores predeterminados.")
        return {"keybind": "N/A", "fov": "N/A"}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: El archivo '{CONFIG_FILE}' no es un JSON válido. Usando valores predeterminados.")
        return {"keybind": "N/A", "fov": "N/A"}
    except Exception as e:
        print(f"Error al cargar '{CONFIG_FILE}': {e}. Usando valores predeterminados.")
        return {"keybind": "N/A", "fov": "N/A"}

def iniciar_rpc():
    """Inicia la conexión de Discord Rich Presence."""
    rpc = None # Initialize rpc to None
    try:
        config = cargar_config()
        print("Intentando conectar con Discord...")
        rpc = Presence(DISCORD_CLIENT_ID)
        rpc.connect()
        print("Conexión con Discord establecida.")

        keybind = config.get("keybind", "N/A")
        fov = config.get("fov", "N/A")
        details = f"KEY [{keybind}] + FOV [{fov}]"

        rpc.update(
            state="VALORANT",
            details=details,
            start=int(time.time()),
            large_image="1",
            large_text="StarHook v3",
            buttons=[{"label": "Discord", "url": "https://discord.gg/EVXfv8VNDP"}],
        )

        print("\nRich Presence cargado exitosamente.")
        print("Tu estado de Discord debería estar actualizado.")
        print("\nPresiona Enter para cerrar el programa...")
        input() # Wait for user input to close

    except Exception as e:
        print(f"\n¡Ha ocurrido un error inesperado!:")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {e}")
        print("\nAsegúrate de que Discord esté abierto y de que el 'Client ID' sea correcto.")
        print("También verifica que el archivo 'config.json' esté en el mismo directorio y sea válido.")
        print("\nPresiona Enter para cerrar el programa y revisar el error...")
        input() # Keep the window open on error
    finally:
        if rpc:
            try:
                rpc.close()
                print("Conexión RPC cerrada.")
            except Exception as e:
                print(f"Error al cerrar la conexión RPC: {e}")

if __name__ == "__main__":
    iniciar_rpc()
