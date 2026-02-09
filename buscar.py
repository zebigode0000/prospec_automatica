from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# LISTA DE EXCLUSÃO (Blacklist) - O robô vai ignorar estas empresas
blacklist = [
    "Marmo Corte", "Penhasco Mármores", "CIM GRANITOS", "Brumagran", "Salvador", 
    "CF Acabamentos", "Topázio Granitos", "Granimaster", "Delta do Brasil", 
    "Vereda Mármores", "Chapa de Granito", "SIGRAMAR", "Internacionale Granite",
    "Dugran", "Mr Pedras", "Polita Natural Stone", "Gramarcal", "Paraná granitos",
    "TrendStone", "SULCAMAR", "Marmoraria Cachoeiro", "São Geraldo", "Tropical Stone",
    "Original Mármores", "RB Mármore", "Top Stone", "Pedregal", "Margran", 
    "Sabadini", "Zatha Stone", "Stone marmoraria", "Creative Mármores", "Larne",
    "rei das pedras", "Sgran Marmores", "Low Price Stone", "M G P Mármores", 
    "Marmoraria GDS", "Brilhante", "Pedras Nobres", "União Ltda", "Marmonito", 
    "Bota Pedras", "Vieira Granitos", "Marmoraria Roma", "CJD GRANITOS", "Breda Ltda",
    "Corteleti", "Fenix", "Rgm granitos", "Marmovix", "Decorato", "Pedras Luminosas",
    "GM Mármores", "Eldorado Ltda", "Marmoraria Vila Velha", "Hanibal", "Rangel Vieira",
    "Inova Ltda", "Guarapedras", "CB & S Granitos", "GRAMIL", "Rezende", "Grupo Braspedras",
    "Vitória Conceito", "Marmoraria Vitoria", "Alto Lage", "Serra Mar", "Fracaroli",
    "Unopedras", "Granito Brasil", "Santana", "Pedras Naturais", "MARMOPLAN", 
    "Suldoeste", "Grauna", "Estevão", "GRAN NOBRE", "Resiliência ART", "Ideal Mármores",
    "Real Pedras", "T&T Mármores", "Grancon", "Petros"
]

def buscar_marmorarias():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://www.google.com.br/maps")
        time.sleep(5) # Pausa para carregar o mapa

        # Tenta achar o campo de busca por múltiplos seletores (ID ou Name)
        try:
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
        except:
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "searchboxinput")))
        
        search_box.send_keys("Marmorarias em Espírito Santo")
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        leads = []
        
        # Scroll para carregar mais resultados
        for i in range(8):
            try:
                scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(2)
            except: pass

        # ... (parte inicial do script igual)
        
        cards = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        print(f"Encontrados {len(cards)} locais. Iniciando extração...")

        for card in cards:
            if len(leads) >= 200: break
            
            try:
                # 1. Tenta pegar o nome primeiro
                nome = card.get_attribute("aria-label")
                
                # 2. Rola até o elemento e clica com força (JS)
                driver.execute_script("arguments[0].scrollIntoView();", card)
                driver.execute_script("arguments[0].click();", card)
                time.sleep(3) # Aumentei o tempo para carregar o painel lateral

                # 3. Tenta pegar o Telefone (Seletor mais aberto)
                try:
                    tel_el = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone:tel:")]')
                    tel = tel_el.get_attribute("data-item-id").replace("phone:tel:", "")
                except:
                    tel = "Telefone não encontrado"

                # 4. Tenta pegar o Site
                try:
                    site_el = driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                    site = site_el.get_attribute("href")
                except:
                    site = "Não tem site"

                # Só adiciona se tiver pelo menos o nome
                if nome:
                    leads.append({
                        "nome": nome,
                        "tel": tel.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""),
                        "site": site,
                        "status": "❌ Sem Site" if site == "Não tem site" else "✅ Possui Site"
                    })
                    print(f"✅ Capturado: {nome}")

            except Exception as e:
                print(f"❌ Erro ao processar um card: {e}")
                continue

        return leads

    finally:
        driver.quit()

meus_leads = buscar_marmorarias()
# ... (fim do seu loop de busca)

# SALVAMENTO CORRETO
with open('dados_leads.js', 'w', encoding='utf-8') as f:
    # Isso cria o ARQUIVO que o HTML vai ler
    f.write("const leads = " + json.dumps(meus_leads, ensure_ascii=False) + ";")

print("\n✅ ARQUIVO 'dados_leads.js' GERADO COM SUCESSO!")
print("Agora abra o seu index.html no navegador.")