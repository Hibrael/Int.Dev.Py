import pyautogui
import time
import sys
import os

def wait_and_click(image_path, timeout=30, confidence=0.7, retry_interval=2):
    """
    Espera até encontrar a imagem na tela e clica no centro dela.
    - timeout: máximo de segundos para esperar.
    - confidence: precisão (0.0 a 1.0) do reconhecimento.
    - retry_interval: pausa entre tentativas.
    """
    
    start = time.time()
    while True:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            x, y = pyautogui.center(location)
            print(x,y)
            pyautogui.click(x, y)
            return True
        else:
            print(f"[DEBUG] '{image_path}' não encontrado ainda... tentando novamente.")
        if time.time() - start > timeout:
            print(f"[ERRO] Não achei {image_path} após {timeout}s.", file=sys.stderr)
            return False
        time.sleep(retry_interval)
cont = 0
if __name__ == "__main__":
    # 1) Tempo para você posicionar a janela certa
    while True:
        print("Coloque a janela em foco. Iniciando em 3s...")
        time.sleep(3)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMG_PATH = os.path.join(BASE_DIR, "botaoimages")
        # 2) Sequência de cliques
        if not wait_and_click(os.path.join(IMG_PATH, 'botao1.png'), timeout=20):
            sys.exit(1)
        time.sleep(3)

        if not wait_and_click(os.path.join(IMG_PATH, 'botao2.png'), timeout=20):
            sys.exit(1)
        time.sleep(1.2)
        
        if not wait_and_click(os.path.join(IMG_PATH,  'botao3.png'), timeout=20):
            sys.exit(1)
        time.sleep(2.3)
        
        if not wait_and_click(os.path.join(IMG_PATH, 'botao4.png'), timeout=20):
            sys.exit(1)
        time.sleep(1)

        if not wait_and_click(os.path.join(IMG_PATH, 'botao5.png'), timeout=20):
            sys.exit(1)
        time.sleep(1)
        cont+=1
        print("Licitações ajustadas: ", cont)

    print("Automação concluída com sucesso!")