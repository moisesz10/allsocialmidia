import csv
import sys
import time
import os
from playwright.sync_api import sync_playwright

def post_community(page, text, schedule_date, schedule_time, publish_now):
    print(f"\n📝 Preparando postagem...")
    
    try:
        try:
            # Tenta encontrar a caixa de texto da comunidade
            input_box = page.locator("div#contenteditable-root").first
            input_box.click(force=True)
            time.sleep(1)
        except Exception:
            print("Caixa de texto não apareceu imediatamente. Tentando clicar no placeholder...")
            page.locator("#commentbox-placeholder").click(force=True)
            time.sleep(1)
            input_box = page.locator("div#contenteditable-root").first
            input_box.click(force=True)
            
        # Limpa o texto caso tenha algo
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        
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
            post_btn = page.locator("ytd-button-renderer#post-button button").first
            if post_btn.is_visible():
                post_btn.click()
            else:
                page.get_by_role("button", name="Postar").click()
            time.sleep(5)
            print("✅ Publicado com sucesso!")
        else:
            print(f"⏰ Agendando para {schedule_date} às {schedule_time}")
            
            # Clica no ícone do relógio para agendar
            # Abre o menu de opções
            action_menu = page.locator("#option-menu button").last
            if action_menu.is_visible():
                action_menu.click()
                time.sleep(1)
                # Clica na última opção (Programar postagem)
                page.locator("tp-yt-paper-item").last.click()
            else:
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
            print("🚀 Conectando ao Chrome já aberto na porta 9222...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            
            page = None
            for p_ in context.pages:
                if 'youtube.com' in p_.url:
                    if 'studio.youtube.com/channel/' in p_.url:
                        import re
                        match = re.search(r'channel/([^/]+)', p_.url)
                        if match:
                            channel_id = match.group(1)
                            print(f"⚠️ Aba do YouTube Studio detectada! Redirecionando para a Comunidade normal...")
                            p_.bring_to_front()
                            p_.goto(f"https://www.youtube.com/channel/{channel_id}/community")
                            time.sleep(4)
                        page = p_
                        break
                    elif 'studio.youtube.com' not in p_.url:
                        page = p_
                        break
                    
            if not page:
                print("❌ Nenhuma aba do YouTube aberta! Por favor, abra a aba da sua Comunidade antes de rodar.")
                return
                
            print("🔗 Aba encontrada! Iniciando automação na aba...")
            page.bring_to_front()
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro ao conectar na porta 9222: {e}")
            print("Certifique-se de iniciar o Chrome com --remote-debugging-port=9222")
            return
        
        for i, post in enumerate(posts):
            is_first_day = (i < 1)
            
            date_str = post['data']
            time_str = post['hora']
            text = post['texto']
            
            print(f"\n📝 Iniciando postagem {i+1}/20...")
            
            # Chama a função que digita e agenda
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
