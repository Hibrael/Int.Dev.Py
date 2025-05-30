import pyautogui
import time
import sys
import keyboard  # pip install keyboard

# Função que clica em uma coordenada com log
def click_at(x, y, delay=1, label=None):
    if label:
        print(f"Clicando em {label} nas coordenadas ({x}, {y})")
    else:
        print(f"Clicando em coordenadas ({x}, {y})")
    pyautogui.click(x, y)
    time.sleep(delay)

if __name__ == "__main__":
    # Coordenadas aproximadas dos botões
    coordenadas_botoes = [
        {"label": "Botão 1", "x": 132, "y": 436, "delay": 3},
        {"label": "Botão 2", "x": 957, "y": 1263, "delay": 1.2},
        {"label": "Botão 3", "x": 847, "y": 1739, "delay": 1.3},
        {"label": "Botão 4", "x": 921, "y": 1274, "delay": 1.5},
        {"label": "Botão 5", "x": 739, "y": 1137, "delay": 1}
    ]

    print("Pressione ESC a qualquer momento para encerrar a automação.")

    while True:
        if keyboard.is_pressed("esc"):
            print("Execução interrompida pelo usuário (ESC pressionado).")
            sys.exit(0)

        print("Coloque a janela em foco. Iniciando em 3s...")
        time.sleep(3)

        for botao in coordenadas_botoes:
            if keyboard.is_pressed("esc"):
                print("Execução interrompida pelo usuário (ESC pressionado).")
                sys.exit(0)

            click_at(botao["x"], botao["y"], delay=botao["delay"], label=botao["label"])

        print("Sequência concluída. Reiniciando...")