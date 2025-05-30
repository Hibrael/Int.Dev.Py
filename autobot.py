import pyautogui
import time
import sys
import os
import cv2
import numpy as np
from PIL import ImageGrab

def match_template_multiscale(needle_path, scales=np.linspace(0.9, 1.1, 7), threshold=0.85):
    screenshot = ImageGrab.grab()
    haystack_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    needle_img = cv2.imread(needle_path)

    for scale in scales:
        resized = cv2.resize(needle_img, (0, 0), fx=scale, fy=scale)
        result = cv2.matchTemplate(haystack_img, resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h, w = resized.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return center_x, center_y, max_val
    return None, None, None

def wait_and_click_smart(image_path, timeout=30, confidence=0.9, threshold_fallback=0.85):
    start = time.time()
    while True:
        # Primeiro tenta com PyAutoGUI
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                x, y = pyautogui.center(location)
                print(f"[OK] '{os.path.basename(image_path)}' encontrado por PyAutoGUI em ({x}, {y})")
                pyautogui.click(x, y)
                return True
        except Exception:
            pass  # se PyAutoGUI falhar, tenta OpenCV

        # Fallback com OpenCV
        x, y, conf = match_template_multiscale(image_path, threshold=threshold_fallback)
        if x and y:
            print(f"[FALLBACK] '{os.path.basename(image_path)}' encontrado por OpenCV em ({x}, {y}) conf {conf:.3f}")
            pyautogui.click(x, y)
            return True

        if time.time() - start > timeout:
            print(f"[ERRO] '{image_path}' não localizado após {timeout}s.", file=sys.stderr)
            return False

        time.sleep(1.5)

cont = 0
if __name__ == "__main__":
    while True:
        print("Coloque a janela em foco. Iniciando em 3s...")
        time.sleep(3)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMG_PATH = os.path.join(BASE_DIR, "botaoimages")

        for i in range(1, 6):
            nome = f'botao{i}.png'
            caminho = os.path.join(IMG_PATH, nome)
            if not wait_and_click_smart(caminho, timeout=20, confidence=0.9, threshold_fallback=0.85):
                sys.exit(1)
            time.sleep(1.5)

        cont += 1
        print("Licitações ajustadas:", cont)
