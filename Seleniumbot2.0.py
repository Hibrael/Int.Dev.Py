import threading
import keyboard
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# CONFIGURAÇÕES
USUARIO = "usuario"
SENHA = "senha"

# Navegador
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

print("[INÍCIO] Acessando o sistema...")
driver.get("https://sistema.prolicitante.com.br/licitacoes/editais/")
time.sleep(3)

# Login
try:
    print("[LOGIN] Preenchendo usuário e senha...")
    wait.until(EC.presence_of_element_located((By.NAME, "usuario"))).send_keys(USUARIO)
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ENTRAR')]"))).click()
    print("[OK] Login realizado.")
except Exception as e:
    print("[ERRO] Falha no login automático:", e)
    driver.quit()
    exit()
# Pausa manual para ajustes
input("🟡 Ajuste manualmente a página e aperte Enter para iniciar a automação...\n")

contador = 0

# Controle de pausa/retomada
pausado = threading.Event()
pausado.set()  # Começa ativo

def monitorar_teclas():
    print("🟡 Pressione 'p' para PAUSAR, 'r' para RETOMAR.")
    while True:
        keyboard.wait('p')
        pausado.clear()
        print("\n⏸️ PAUSADO. Pressione 'r' para RETOMAR...\n")
        keyboard.wait('r')
        pausado.set()
        print("▶️ RETOMADO.")

threading.Thread(target=monitorar_teclas, daemon=True).start()

# Funções de clique
def clicar_por_ng_click(ng_click):
    try:
        el = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[@ng-click=\"{ng_click}\"]")))
        el.click()
        print(f"[OK] Clique via ng-click='{ng_click}' realizado.")
        return True
    except Exception as e:
        print(f"[ERRO] ng-click '{ng_click}' não encontrado. {e}")
        driver.save_screenshot(f"erro_{ng_click.replace('()', '')}.png")
        return False

def aguardar_e_clicar_no_icone(timeout=60):
    try:
        print("[AGUARDANDO] Ícone da varinha mágica aparecer...")
        icone = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//md-icon[@aria-label='icon-auto-fix']"))
        )
        ActionChains(driver).move_to_element(icone).click().perform()
        print("[OK] Clique no botão com ícone (varinha) realizado.")
        return True
    except Exception as e:
        print("[ERRO] Botão com ícone não encontrado após aguardar:", e)
        driver.save_screenshot("erro_varinha.png")
        return False
    

# Antes do loop:
licitacao_info = []  # lista para armazenar {'id': ..., 'objeto': ...}

try:
    # Loop principal
    while True:
        pausado.wait()
        print(f"\n Iniciando novo ciclo...")

        if not aguardar_e_clicar_no_icone():
            print("[INFO] Ícone da varinha não encontrado. Provavelmente sem mais licitações.")
            break
        time.sleep(2.5)

        if not clicar_por_ng_click("vm.visualizarItensPortal()"):
            break
        time.sleep(1.5)

        if not clicar_por_ng_click("dialog.hide()"):
            break
        time.sleep(1.5)

        if not clicar_por_ng_click("vm.salvar()"):
            break
        time.sleep(1.5)

        # ─── Extrair ID e Objeto ───
        try:
            span_id = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//span[@ng-if=\"!vm.dados.id_categoria\"]")
            ))
            texto_id = span_id.text
            id_num = texto_id.split(" - ")[0].strip()

            div_objeto = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@ng-if=\"vm.licitacao.objeto\"]")
            ))
            texto_objeto = div_objeto.text
            objeto_desc = texto_objeto.replace("Objeto: ", "").strip()

            licitacao_info.append({"id": id_num, "objeto": objeto_desc})
            print(f"[OK] Coletado ID={id_num} com Objeto=\"{objeto_desc}\"")
        except Exception as e:
            print("[ERRO] Não consegui extrair ID e/ou Objeto:", e)
            driver.save_screenshot("erro_extrair_info.png")
            pausado.clear()
            print("\n⏸️ PAUSADO. Pressione 'r' para RETOMAR...\n")
            keyboard.wait('r')
            pausado.set()

        # 5) TENHO CERTEZA (último clique)
        if not clicar_por_ng_click("dialog.hide()"):
            break
        time.sleep(2)

        contador += 1
        print(f"[✓] Licitações ajustadas: {contador}")
        print("[AGUARDANDO] Próximo ciclo em 3 segundos...\n")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n[INFO] Execução interrompida pelo usuário (Ctrl+C).")

finally:
    # 1) Monta um DataFrame a partir de licitacao_info
    df = pd.DataFrame(licitacao_info)

    # 2) Salva em arquivo Excel
    caminho_excel = "licitacoes_ajustadas.xlsx"
    df.to_excel(caminho_excel, index=False, header=["ID", "Objeto"])
    print(f"\n[OK] Arquivo Excel gerado em: {caminho_excel}")

    # 3) Opcional: também exibe no terminal
    print("\nLista de licitações ajustadas:")
    print(f"\n Quantidade de licitações ajustadas: {contador}\n")
    for info in licitacao_info:
        print(f" - ID: {info['id']}  |  Objeto: {info['objeto']}\n")

    driver.quit()
    exit()





