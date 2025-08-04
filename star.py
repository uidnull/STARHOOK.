##6985368251046219728696
##8445743096395328289706
##4123304751600872055608
##5531653824141569916013
##8607304540948031064764
##3936345961089001280750
##6838195097086206064917
##3273459709103835067669
##4578808608711074471577
##2385479647335732569556
##3304173240993875620753
##3586848485092125142788
##3159097110389283635591
##7461079450631171307458
##8982703233217467407999
##8958620883920856932860
##6530459849614859941958
##6233203912297430597595
##1384268832588676742809
##4461125900671559455901
##2323460876139116292891
##2278579271640861788424
##2814092309641521256332
##6919043119219155861438
##9342209684067275319414
UUID = "03e0959e18fb46029d868b405e368ade"

import cv2
import time
import numpy
import win32api
import threading
import bettercam
from multiprocessing import Queue, Process
from ctypes import windll
import os
import json
import tempfile
import numpy as np
from colorama import init, Fore, Back, Style
init(autoreset=True)

CYAN = Fore.CYAN + Style.BRIGHT

def bypass(queue):
    temp_trigger_file = os.path.join(tempfile.gettempdir(), "m83brhkeu84902.txt")
    print(CYAN + f"[*] Songs playing successfully")

    while True:
        signal = queue.get()
        if signal == "Shoot":
            try:
                with open(temp_trigger_file, 'w') as f:
                    f.write("shoot")
            except PermissionError as e:
                print(CYAN + f"[!] Permission denied writing to {temp_trigger_file}: {e}")
                # Aquí puedes decidir si crear un archivo alternativo o simplemente continuar
                # Por ejemplo, podrías intentar un archivo con nombre distinto para no bloquear el flujo
                alt_file = os.path.join(tempfile.gettempdir(), "m83brhkeu84902_alt.txt")
                try:
                    with open(alt_file, 'w') as f:
                        f.write("shoot")
                    print(CYAN + f"[*] Wrote to alternate file {alt_file}")
                except Exception as e2:
                    print(CYAN + f"[!] Failed writing alternate file: {e2}")
                # Continúa sin detener el proceso

## zkIu3Xg8v@7$Yd!rP%z21b6Q9o*UfN0c
## 9aF##3570115288937968606772xB4C8_22zzkA1vT!mp6M2Lg$qD
## !!@r8Gv##x509a**]kL29sdqpZ^!wE
## <Z3Q>--7nP_mNx=!##@8^Rp0x1A2C

class Triggerbot:
    def __init__(self, queue, keybind, base_fov, hsv_ranges, shooting_rate, fps):
        self.queue = queue
        self.keybind = keybind
        self.base_fov = base_fov
        self.hsv_ranges = [
            (np.array(hsv_min, dtype=np.uint8), np.array(hsv_max, dtype=np.uint8))
            for hsv_min, hsv_max in hsv_ranges
        ]
        self.shooting_rate = shooting_rate
        self.fps = fps

        self.last_width = 0
        self.last_height = 0
        self.camera = None
        self.check_region = None

## 0040FFAC::==!X2gy@77!!kPv3498
## $crPyD_**7N##8550203698541448619239f&*z6q0Xx999001F
## &&@__XKP93####2149873740044499085155lm!tY7sdAq##Zt##t##
## 9911-FFEF-340C-XaPZ--kL$@gBt!!
## ___noise123__##$$__FFAB9987__!!
## >>>[x9Y]:::440xZZ!##$$~qT3mv88
## //junk_data_zone::abcd9921%%Zk
## s0Pa99s$$Z@9203k_Lv!qq2Wz0011

    def update_resolution_and_camera(self):
        user32 = windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        if width != self.last_width or height != self.last_height or self.camera is None:
            ## Stop and delete previous camera
            if self.camera:
                try:
                    self.camera.stop()
                except Exception as e:
                    print(CYAN + f"[!] Error stopping song: {e}")
                del self.camera
                time.sleep(0.3)  ## Let OS release camera handle

            self.last_width = width
            self.last_height = height

            scale_x = width / 1920
            scale_y = height / 1080
            scale = (scale_x + scale_y) / 2
            scaled_fov = int(self.base_fov * scale)

            center_x = width // 2
            center_y = height // 2
            self.check_region = (
                center_x - scaled_fov,
                center_y - scaled_fov,
                center_x + scaled_fov,
                center_y + scaled_fov,
            )

            try:
                self.camera = bettercam.create(output_idx=0, region=self.check_region)
                self.camera.start(target_fps=self.fps)
                print(CYAN + f"[*] Sound quality changed: {width}x{height} | Song number: {scaled_fov}")
            except Exception as e:
                print(CYAN + f"[!] Failed to play song: {e}")
                self.camera = None

    def Color(self):
        hsv = cv2.cvtColor(self.camera.get_latest_frame(), cv2.COLOR_RGB2HSV)
        for cmin, cmax in self.hsv_ranges:
            mask = cv2.inRange(hsv, cmin, cmax)
            if np.any(mask):
                return True
        return False

## ||@noise__X_P@13370xF_Z&d$@####
## <<<<<<<Yzv0x00112233AABBCCDD
## s!gn_ch@ng3::8844kppWQ##tLm0202
## ####xxFF1244009_Mask#############m#!!
# random_noise##2306855562583629679835a3vQz!!XpL5q
# %%%F1r3h0l3%%--xABC0023aa12
# q99X--midSig##3797153691823972181269XxYyZz__!

    def Main(self):
        while True:
            self.update_resolution_and_camera()
            if self.camera:
                try:
                    if win32api.GetAsyncKeyState(self.keybind) < 0 and self.Color():
                        self.queue.put("Shoot")
                        time.sleep(self.shooting_rate / 1000)
                except Exception as e:
                    print(CYAN + f"[!] Detection error: {e}")
            time.sleep(0.001)

def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

if __name__ == "__main__":
    print(CYAN + "[*] Musicbot starting...")
    queue = Queue()
    p = Process(target=bypass, args=(queue,))
    p.start()

    config = load_config()
    print(CYAN + "[*] Songs loaded")

    triggerbot = Triggerbot(
        queue,
        config['keybind'],
        config['fov'],  # base vol 100%
        config['hsv_ranges'],  # ✅ soporte multisongs
        config['shooting_rate'],
        config['fps']
    )

    threading.Thread(target=triggerbot.Main, daemon=True).start()
    print(CYAN + "[*] Musicbot active")
    p.join()

# zkIu3Xg8v@7$Yd!rP%z21b6Q9o*UfN0c
# 9aF#4908098459762269875407xB4C8_22zzkA1vT!mp6M2Lg$qD
# !!@r8Gv#x509a**]kL29sdqpZ^!wE
# <Z3Q>--7nP_mNx=!#@8^Rp0x1A2C
# 0040FFAC::==!X2gy@77!!kPv3498
# $crPyD_**7N#4668221865134711479033f&*z6q0Xx999001F
# &&@__XKP93##2367837247643869513608lm!tY7sdAq#Zt#t#
# 9911-FFEF-340C-XaPZ--kL$@gBt!!
# ___noise123__#$$__FFAB9987__!!
# >>>[x9Y]:::440xZZ!#$$~qT3mv88
# //junk_data_zone::abcd9921%%Zk
# s0Pa99s$$Z@9203k_Lv!qq2Wz0011
# xFFAA3411##comment_anti_sig#
# ||@noise__X_P@13370xF_Z&d$@##
# <<<<<<<Yzv0x00112233AABBCCDD
# s!gn_ch@ng3::8844kppWQ#tLm0202
# ##xxFF1244009_Mask#######m#!!
# random_noise##8497472853059515702602a3vQz!!XpL5q
# %%%F1r3h0l3%%--xABC0023aa12
## q99X--midSig####6517734318967539296304XxYyZz__!

UUID = "03e0959e18fb46029d868b405e368ade"
##2683952600434012904046
##7146252753039852577924
##8054516168620586942492
##3485287348117428230328
##1920572813915222697743
##5693348393953261423083
##1224784561735032536859
##7583234727354120214694
##6133178772393230797035
##2267735911081039215857
##9254493527978450386485
##8347365832184714372241
##3443323405604163309845
##7872880000058832068677
##4677117632752991787667
##8215578504624280090411
##6123435209003485680538
##6732210013640434205941
##1715347624108723696965
##8763114053674739150330
##3018120630729056276788
##5775320246902298203418
##8557805686748892914240
##3560159039598660985846
##7856419648023621684498
