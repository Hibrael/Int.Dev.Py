import threading
import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# CONFIGURAÇÕES
USUARIO = "Hibrael.xavier"
SENHA = "Kcas500@"

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

# Loop principal
while True:
    pausado.wait()  # Espera estar no estado 'retomado'
    print(f"\n Iniciando novo ciclo...")

    if not aguardar_e_clicar_no_icone():
        break
    time.sleep(2.5)

    if not clicar_por_ng_click("vm.visualizarItensPortal()"):
        break
    time.sleep(1.5)

    if not clicar_por_ng_click("dialog.hide()"):  # USAR COMO ESPELHO
        break
    time.sleep(1.5)

    if not clicar_por_ng_click("vm.salvar()"):
        break
    time.sleep(1.5)

    if not clicar_por_ng_click("dialog.hide()"):  # TENHO CERTEZA
        break
    time.sleep(2)

    contador += 1
    print(f"[✓] Licitações ajustadas: {contador}")
    print("[AGUARDANDO] Próximo ciclo em 3 segundos...\n")
    time.sleep(2)
