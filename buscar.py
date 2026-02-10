from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def buscar_marmorarias():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://www.google.com.br/maps")
        time.sleep(5)

        try:
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
        except:
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "searchboxinput")))
        
        search_box.send_keys("Marmorarias em Santos")
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        # --- AJUSTE 1: SCROLL MAIS PROFUNDO ---
        print("Iniciando rolagem profunda para carregar mais de 100 resultados...")
        for i in range(25):  # Aumentado de 8 para 25 para carregar muito mais locais
            try:
                scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(2) # Tempo para o Google carregar novos cards
                if i % 5 == 0:
                    print(f"Rolagem {i} concluída...")
            except: pass

        # Captura todos os cards carregados após a rolagem longa
        cards = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        total_encontrado = len(cards)
        print(f"Total de locais carregados no painel: {total_encontrado}")
        
        leads = []

        # --- AJUSTE 2: PROCESSAR TODOS OS CARDS ENCONTRADOS ---
        for index, card in enumerate(cards):
            # Limite de segurança aumentado para 300
            if len(leads) >= 300: break 
            
            try:
                nome = card.get_attribute("aria-label")
                
                # Scroll individual para o card ficar visível antes do clique
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", card)
                
                # --- AJUSTE 3: ESPERA DINÂMICA PELOS DADOS ---
                # Aguarda o painel lateral atualizar com o novo nome
                time.sleep(2.5) 

                # Extração do Telefone
                try:
                    tel_el = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone:tel:")]')
                    tel = tel_el.get_attribute("data-item-id").replace("phone:tel:", "")
                except:
                    tel = "Telefone não encontrado"

                # Extração do Site
                try:
                    site_el = driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                    site = site_el.get_attribute("href")
                except:
                    site = "Não tem site"

                if nome:
                    leads.append({
                        "nome": nome,
                        "tel": tel.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""),
                        "site": site,
                        "status": "❌ Sem Site" if site == "Não tem site" else "✅ Possui Site"
                    })
                    print(f"✅ [{len(leads)}] Capturado: {nome}")

            except Exception as e:
                continue

        return leads

    finally:
        driver.quit()

meus_leads = buscar_marmorarias()

with open('dados_leads.js', 'w', encoding='utf-8') as f:
    f.write("const leads = " + json.dumps(meus_leads, ensure_ascii=False) + ";")

print(f"\n✅ SUCESSO! {len(meus_leads)} leads salvos em 'dados_leads.js'.")