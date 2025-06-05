import threading
import keyboard
import pandas as pd
import time
import os
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from selenium import webdriver
from openpyxl.styles import Font
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# CONFIGURAÇÕES
USUARIO = "Hibrael.xavier"
SENHA = "Kcas500@"


# Navegador
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
wait = WebDriverWait(driver, 20)

print("[INÍCIO] Acessando o sistema...")
driver.get("https://sistema.prolicitante.com.br/licitacoes/editais/")
time.sleep(3)

# Login
try:
    print("[LOGIN] Preenchendo usuário e senha...")
    wait.until(EC.presence_of_element_located((By.NAME, "usuario"))).send_keys(USUARIO)
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(SENHA)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ENTRAR')]"))
    ).click()
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
        keyboard.wait("p")
        pausado.clear()
        print("\n⏸️ PAUSADO. Pressione 'r' para RETOMAR...\n")
        keyboard.wait("r")
        pausado.set()
        print("▶️ RETOMADO.")


threading.Thread(target=monitorar_teclas, daemon=True).start()

# Funções de clique
def clicar_por_ng_click(ng_click):
    try:
        el = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//*[@ng-click=\"{ng_click}\"]"))
        )
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
            span_id = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//span[@ng-if=\"!vm.dados.id_categoria\"]")
                )
            )
            texto_id = span_id.text
            id_num = texto_id.split(" - ")[0].strip()

            div_objeto = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@ng-if=\"vm.licitacao.objeto\"]")
                )
            )
            texto_objeto = div_objeto.text
            objeto_desc = texto_objeto.replace("Objeto: ", "").strip()

            licitacao_info.append({"id": id_num, "objeto": objeto_desc})
            print(f"[OK] Coletado ID={id_num} com Objeto=\"{objeto_desc}\"")
        except Exception as e:
            print("[ERRO] Não consegui extrair ID e/ou Objeto:", e)
            driver.save_screenshot("erro_extrair_info.png")
            pausado.clear()
            print("\n⏸️ PAUSADO. Pressione 'r' para RETOMAR...\n")
            keyboard.wait("r")
            pausado.set()

        # 5) TENHO CERTEZA (último clique)
        if not clicar_por_ng_click("dialog.hide()"):
            break
        time.sleep(2)

        contador += 1
        print(f"Licitações ajustadas: {contador}")
        print("[AGUARDANDO] Próximo ciclo em 3 segundos...\n")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n[INFO] Execução interrompida pelo usuário (Ctrl+C).")


finally:
    # 1) Monta um DataFrame a partir de licitacao_info e renomeia colunas
    df = pd.DataFrame(licitacao_info)
    df.rename(columns={"id": "ID", "objeto": "Objeto"}, inplace=True)

    # 2) Define pasta de destino e garante que exista
    pasta_destino = r"C:\Users\Hibrael.xavier\Desktop\Ajuste_Seleniumbot"
    os.makedirs(pasta_destino, exist_ok=True)

    # 3) Gera um sufixo com timestamp para diferenciar cada execução
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_base = f"licitacoes_ajustadas_{timestamp}"
    caminho_excel = os.path.join(pasta_destino, f"{nome_base}.xlsx")

    # 4) Lê (ou cria) o keywords.txt
    arquivo_keywords = os.path.join(pasta_destino, "keywords.txt")
    if not os.path.exists(arquivo_keywords):
        with open(arquivo_keywords, "w", encoding="utf-8") as f:
            f.write("# Insira uma palavra‐chave por linha\n")
        print(f"[INFO] '{arquivo_keywords}' não encontrado. Criado arquivo vazio para palavras‐chave.")

    with open(arquivo_keywords, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        palavras_chave = [
            linha.strip()
            for linha in linhas
            if linha.strip() and not linha.strip().startswith("#")
        ]

    if not palavras_chave:
        print(f"[AVISO] '{arquivo_keywords}' vazio ou só comentários. Nenhum destaque será aplicado.")

    # 5) Monta o regex a partir da lista lida
    if palavras_chave:
        # Substituímos espaço por '\s*' para capturar variações (opcional)
        regex = "|".join([p.replace(" ", r"\s*") for p in palavras_chave])
    else:
        regex = None

        # 6) Escreve o DataFrame inteiro usando XlsxWriter
    with pd.ExcelWriter(caminho_excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")
        workbook  = writer.book
        worksheet = writer.sheets["Dados"]

        # 7) Define formatos de fonte
        fmt_preto    = workbook.add_format({"font_color": "000000"})
        fmt_cinza     = workbook.add_format({"font_color": "D9D9D9"}) 
        fmt_verde    = workbook.add_format({"font_color": "008000"})
        fmt_vermelho = workbook.add_format({"font_color": "FF0000"})

        col_indice_objeto = 1  # a coluna B no Excel (índice 1)

        # 8) Percorre cada linha do DataFrame e aplica rich string na célula “Objeto”
        if regex:
            import re
            padrao = re.compile(regex, flags=re.IGNORECASE)

            for df_idx, texto in enumerate(df["Objeto"]):
                m = padrao.search(texto)
                if not m:
                    # Sem correspondência → mantém texto inteiro em preto
                    worksheet.write(df_idx + 1, col_indice_objeto, texto, fmt_cinza)
                    continue

                # Se encontrou palavra‐chave, fragmenta o texto em 3 partes:
                #   A) antes_da_palavra  (verde)
                #   B) a_própria_palavra (vermelho)
                #   C) depois_da_palavra (verde)
                partes = []
                pos = 0
                for match in padrao.finditer(texto):
                    start, end = match.span()
                    # trecho anterior à palavra‐chave
                    if start > pos:
                        partes.append((fmt_verde, texto[pos:start]))
                    # palavra‐chave (em vermelho)
                    partes.append((fmt_vermelho, texto[start:end]))
                    pos = end

                # resto do texto após a última correspondência
                if pos < len(texto):
                    partes.append((fmt_verde, texto[pos:]))

                # Monta a lista de argumentos para write_rich_string:
                # deve ser: [formato1, string1, formato2, string2, ...]
                rich_args = []
                for fmt, trecho in partes:
                    rich_args.append(fmt)
                    rich_args.append(trecho)

                # E escreve tudo de uma vez
                worksheet.write_rich_string(df_idx + 1,
                                           col_indice_objeto,
                                           *rich_args)
        else:
            # Se não houver regex, deixa todas as células "Objeto" em cinza
            for df_idx, texto in enumerate(df["Objeto"]):
                worksheet.write(df_idx + 1, col_indice_objeto, texto, fmt_cinza)

        # Ajusta largura da coluna “Objeto” para caber o texto
        worksheet.set_column(col_indice_objeto, col_indice_objeto, 50)

    # Ao sair do bloco 'with', o arquivo é salvo automaticamente
    print(f"\n[OK] Arquivo Excel gerado com destaque de palavras-chave: {caminho_excel}")

    # 9) Exibe no terminal o total de licitações ajustadas
    print(f"Total de licitações ajustadas: {contador}")

    driver.quit()
    exit()