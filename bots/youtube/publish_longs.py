import csv
import sys
import time
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def upload_video(page, video_path, title, description, schedule_date, schedule_time, publish_now=False):
    print(f"\n🎬 Iniciando upload de: {title}")
    
    # Go to YouTube Studio Dashboard
    page.goto("https://studio.youtube.com/", wait_until="load", timeout=60000)
    time.sleep(3)
    
    # Captura o ID do canal em que o navegador está logado no momento
    current_url = page.url
    if "/channel/" in current_url:
        channel_id = current_url.split("/channel/")[1].split("/")[0]
        upload_url = f"https://studio.youtube.com/channel/{channel_id}/videos/upload?d=ud"
        page.goto(upload_url, wait_until="load", timeout=60000)
    else:
        # Fallback caso a URL seja diferente
        page.locator("ytcp-button#create-icon").click()
        time.sleep(1)
        page.locator("tp-yt-paper-item#text-item-0").click()
        
    time.sleep(3)
    
    # Upload the video file by directly attaching to the hidden input
    print(f"Enviando arquivo: {video_path}")
    try:
        page.locator("input[type=file]").set_input_files(video_path, timeout=20000)
    except Exception as e:
        print(f"Erro ao selecionar arquivo: {e}")
        return False
        
    # Aguardar o modal inicializar e o YouTube extrair o nome do arquivo
    print("⏳ Aguardando modal estabilizar...")
    time.sleep(10)
    
    # Fill Title
    print("Preenchendo Título...")
    try:
        title_box = page.locator("div#textbox").first
        title_box.click(force=True, timeout=10000)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.keyboard.type(title, delay=30)
        time.sleep(0.5)
        page.evaluate("""() => {
            const b = document.querySelectorAll('div#textbox')[0];
            if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
        }""")
    except Exception as e:
        print(f"Erro ao preencher título: {e}")
        
    # Fill Description
    print("Preenchendo Descrição...")
    try:
        desc_box = page.locator("div#textbox").nth(1)
        desc_box.click(force=True, timeout=10000)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.keyboard.type(description, delay=10)
        time.sleep(0.5)
        page.evaluate("""() => {
            const b = document.querySelectorAll('div#textbox')[1];
            if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
        }""")
    except Exception as e:
        print(f"Erro ao preencher descrição: {e}")
        
    # Is it made for kids? No.
    print("Marcando 'Não é conteúdo para crianças'...")
    try:
        page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click(force=True, timeout=5000)
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao marcar NOT FOR KIDS: {e}")
        
    # Click Next until the Visibility tab
    print("Avançando para a aba de Visibilidade...")
    for attempt in range(10):
        try:
            sched = page.locator("tp-yt-paper-radio-button[name='SCHEDULE']")
            if sched.is_visible(timeout=1000):
                print("✅ Aba Visibility encontrada!")
                break
        except Exception:
            pass

        try:
            next_btn = page.locator("ytcp-button#next-button")
            if next_btn.is_visible(timeout=1000) and next_btn.is_enabled(timeout=1000):
                next_btn.click(force=True)
                time.sleep(3)
        except Exception:
            pass
            
    # Schedule (Agendar) ou Publicar
    if publish_now:
        print("Publicando imediatamente (AGORA)!")
        try:
            page.locator("tp-yt-paper-radio-button[name='PUBLIC']").click()
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao publicar: {e}")
    else:
        print(f"Agendando para: {schedule_date} às {schedule_time}")
        try:
            # Click "Schedule" radio button
            page.locator("tp-yt-paper-radio-button[name='SCHEDULE']").click()
            time.sleep(1)
            
            # Set date
            datepicker = page.locator("ytcp-text-dropdown-trigger#datepicker-trigger")
            datepicker.click()
            page.keyboard.press("Control+A")
            page.keyboard.insert_text(schedule_date)
            page.keyboard.press("Enter")
            time.sleep(1)
            
            # Set time
            timepicker = page.locator("ytcp-text-dropdown-trigger#time-of-day-trigger")
            timepicker.click()
            page.keyboard.press("Control+A")
            page.keyboard.insert_text(schedule_time)
            page.keyboard.press("Enter")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao agendar: {e}")
        
    # Click Schedule button
    print("Finalizando agendamento...")
    try:
        page.click("ytcp-button#done-button")
        time.sleep(5)
        # Close the success dialog
        page.click("ytcp-button#close-button")
        print("✅ Vídeo agendado com sucesso!")
        return True
    except Exception as e:
        print("Erro ao concluir agendamento.")
        return False


def run_bot(csv_path):
    print("Iniciando Robô Publicador...")
    
    # Determinar datas começando de hoje
    current_day = datetime.now()
    
    videos = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            videos.append(row)
            
    if not videos:
        print("Nenhum vídeo encontrado no CSV.")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Conectado ao navegador Chrome já aberto!")
            context = browser.contexts[0]
            page = None
            for p_ in context.pages:
                if 'studio.youtube.com' in p_.url:
                    page = p_
                    break
            if not page:
                page = context.new_page()
        except Exception as e:
            print(f"Erro ao conectar na porta 9222: {e}. Certifique-se de iniciar o Chrome com --remote-debugging-port=9222")
            return
            
            
        def handle_dialog(d):
            print(f"💬 Dialog auto-dismiss: {d.message[:60]}")
            d.accept()
        page.on("dialog", handle_dialog)
        
        # Foca apenas em vídeos longos
        longs = [v for v in videos if 'long' in v['video_id']]
        
        for i, long_vid in enumerate(longs):
            is_first_day = (i == 0)
            date_str = current_day.strftime("%d/%m/%Y")
            
            # Longos às 19:00
            desc = long_vid['legenda_post'] + "\n\n" + long_vid['hashtags']
            video_path = os.path.abspath(long_vid['caminho_arquivo_video'])
            upload_video(page, video_path, long_vid['titulo'], desc, date_str, "19:00", publish_now=is_first_day)
            time.sleep(5)
            
            current_day += timedelta(days=1)
            
        print("🎉 Todos os Vídeos Longos foram agendados!")
        page.close()

if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'data/cronograma_21_posts.csv'
    run_bot(csv_path)
