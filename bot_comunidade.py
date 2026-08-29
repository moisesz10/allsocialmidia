import csv
import sys
import time
import os
from playwright.sync_api import sync_playwright

def post_community(page, text, schedule_date, schedule_time, publish_now):
    print(f"\n📝 Preparando postagem...")
    
    try:
        # Tenta encontrar a caixa de texto da comunidade
        input_box = page.locator("div#contenteditable-root").first
        try:
            input_box.wait_for(state="visible", timeout=10000)
        except:
            print("Caixa de texto não apareceu imediatamente. Tentando clicar no placeholder...")
            try:
                page.locator("ytd-backstage-post-creation-renderer").click()
                time.sleep(2)
            except:
                pass
            
        input_box.click(force=True)
        time.sleep(1)
        
        # Limpa e digita
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        
        # Digita o texto linha por linha para respeitar as quebras
        for line in text.split('\n'):
            page.keyboard.type(line, delay=5)
            page.keyboard.press("Shift+Enter")
        time.sleep(1)
        
        # Dispara evento de input para o YouTube registrar
        page.evaluate("""() => {
            const b = document.querySelectorAll('div#contenteditable-root')[0];
            if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
        }""")
        
        time.sleep(2)
        
        if publish_now:
            print("🚀 Publicando AGORA!")
            post_btn = page.locator("ytd-button-renderer#submit-button").first
            if post_btn.is_visible():
                post_btn.click()
            else:
                page.get_by_role("button", name="Postar").click()
            time.sleep(5)
            print("✅ Publicado com sucesso!")
        else:
            print(f"⏰ Agendando para {schedule_date} às {schedule_time}")
            
            # Clica no ícone do relógio para agendar
            schedule_icon = page.locator("ytd-button-renderer#schedule-button").first
            if schedule_icon.is_visible():
                schedule_icon.click()
            else:
                page.get_by_role("button", name="Programar").first.click()
                
            time.sleep(2)
            
            # Preenche a data
            datepicker = page.locator("ytcp-text-dropdown-trigger#datepicker-trigger")
            datepicker.click()
            time.sleep(1)
            page.keyboard.press("Control+A")
            page.keyboard.insert_text(schedule_date)
            page.keyboard.press("Enter")
            time.sleep(1)
            
            # Preenche a hora
            timepicker = page.locator("ytcp-text-dropdown-trigger#time-of-day-trigger")
            timepicker.click()
            time.sleep(1)
            page.keyboard.press("Control+A")
            page.keyboard.insert_text(schedule_time)
            page.keyboard.press("Enter")
            time.sleep(1)
            
            # Clica no botão final de agendar no modal
            # O botão de agendar dentro do modal de agendamento pode ter um ID específico
            modal_schedule_btn = page.locator("ytcp-button#submit-button")
            if modal_schedule_btn.is_visible():
                modal_schedule_btn.click()
            else:
                page.get_by_role("button", name="Programar").nth(1).click()
                
            time.sleep(5)
            print("✅ Agendado com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao postar: {e}")

def run_bot(csv_path):
    print("🤖 Iniciando Robô da Comunidade na guia atual...")
    
    posts = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
            
    if not posts:
        print("Nenhuma postagem encontrada no CSV.")
        return

    with sync_playwright() as p:
        try:
            print("🚀 Abrindo Chrome para automação com seu perfil logado...")
            context = p.chromium.launch_persistent_context(
                user_data_dir="/home/moises/work/allsocialmidia/chrome_profile",
                channel="chrome",
                headless=False,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = context.pages[0]
            
            print("🌍 Navegando para o YouTube Studio...")
            page.goto("https://studio.youtube.com/")
            
            page.wait_for_selector("button#avatar-btn", timeout=30000)
            
            print("🌍 Capturando o arroba do canal...")
            page.locator("button#avatar-btn").click()
            time.sleep(2)
            popup_text = page.locator("ytd-active-account-header-renderer").inner_text()
            
            import re
            match = re.search(r'@[A-Za-z0-9_-]+', popup_text)
            if match:
                handle = match.group(0)
                community_url = f"https://www.youtube.com/{handle}/community"
                print(f"🔗 Handle encontrado: {handle}")
                print(f"➡️ Acessando a guia comunidade: {community_url}")
                page.goto(community_url)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
            else:
                print("❌ Não foi possível encontrar o handle (arroba) do canal.")
                return
                
        except Exception as e:
            print(f"Erro ao iniciar Chrome ou acessar a página: {e}")
            return
        
        for i, post in enumerate(posts):
            is_first_day = (i < 2) # As duas primeiras postagens são hoje (agora)
            
            date_str = post['data']
            time_str = post['hora']
            text = post['texto']
            
            post_community(page, text, date_str, time_str, publish_now=is_first_day)
            
            # Recarrega a página para o próximo post para limpar o formulário
            page.reload()
            time.sleep(5)
            
        print("🎉 Todas as postagens foram processadas!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python bot_comunidade.py <caminho_do_csv>")
        sys.exit(1)
        
    run_bot(sys.argv[1])
