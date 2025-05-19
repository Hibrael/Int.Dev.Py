from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# CONFIGURAÇÃO DO DRIVER
caminho_driver = r"C:\selenium\chromedriver.exe"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(caminho_driver), options=options)

# ACESSA O SISTEMA
driver.get("https://sistema.prolicitante.com.br/licitacoes/editais/")

# AGUARDA LOGIN MANUAL
input("⚠️ Faça login e pressione ENTER para continuar...")

# ENCONTRA E CLICA NO BOTÃO ESPECÍFICO
try:
    botoes = driver.find_elements(By.XPATH, "//button[contains(@ng-click, 'ajustarItens')]")

    for botao in botoes:
        ngclick = botao.get_attribute('ng-click')
        print(f"Botão encontrado: {ngclick}")
        if "1313160" in ngclick:
            driver.execute_script("arguments[0].click();", botao)  # clique seguro via JS
            print("✅ Clique executado no botão com ID 1313160.")

            # AGUARDA O MODAL E CLICA NO BOTÃO "ITENS PORTAL"
            print("⏳ Aguardando botão 'ITENS PORTAL' aparecer...")
            botao_itens_portal = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ITENS PORTAL')]"))
            )
            botao_itens_portal.click()
            print("✅ Clique no botão 'ITENS PORTAL' realizado com sucesso.")
            time.sleep(2)

            try:
                print("🔍 URL atual:", driver.current_url)
                print("🔍 Título da página:", driver.title)
            except:
                print("⚠️ A aba já foi fechada.")
            break

    else:
        print("⚠️ Nenhum botão com o ID 1313160 foi encontrado.")

except Exception as e:
    print(f"❌ Erro ao localizar ou clicar no botão: {e}")