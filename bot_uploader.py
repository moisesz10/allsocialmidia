import csv
import sys
import time
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def upload_video(page, video_path, title, description, schedule_date, schedule_time):
    print(f"\n🎬 Iniciando upload de: {title}")
    
    # Go to YouTube Studio Dashboard
    page.goto("https://studio.youtube.com/", wait_until="networkidle")
    time.sleep(3)
    
    # Direct upload URL bypassing the Create button
    page.goto("https://studio.youtube.com/channel/UC1hr6pLEGC8PN_Yh0T8ZOTA/videos/upload?d=ud", wait_until="networkidle")
    time.sleep(3)
    
    # Upload the video file by directly attaching to the hidden input
    print(f"Enviando arquivo: {video_path}")
    try:
        page.locator("input[type=file]").set_input_files(video_path)
    except Exception as e:
        print(f"Erro ao selecionar arquivo: {e}")
        return False
        
    time.sleep(10) # Wait for the upload modal to fully load and process
    
    # Fill Title
    print("Preenchendo Título...")
    try:
        title_box = page.locator("div#textbox").nth(0)
        title_box.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.insert_text(title)
    except Exception as e:
        print("Erro ao preencher título.")
    
    # Fill Description
    print("Preenchendo Descrição...")
    try:
        desc_box = page.locator("div#textbox").nth(1)
        desc_box.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.insert_text(description)
    except Exception as e:
        print("Erro ao preencher descrição.")
        
    # Is it made for kids? No.
    print("Marcando 'Não é conteúdo para crianças'...")
    try:
        page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click()
    except:
        pass
        
    # Click Next until the Visibility tab
    print("Avançando para a aba de Visibilidade...")
    for _ in range(3):
        try:
            page.click("ytcp-button#next-button")
            time.sleep(2)
        except:
            break
            
    # Schedule (Agendar)
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
    
    # Determinar datas começando de amanhã
    amanha = datetime.now() + timedelta(days=1)
    
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
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Conectado ao navegador Chrome!")
            
            context = browser.contexts[0]
            page = context.new_page()
            
            current_day = amanha
            
            for i in range(0, len(videos), 2):
                short_vid = videos[i] if i < len(videos) and 'short' in videos[i]['video_id'] else None
                long_vid = videos[i+1] if i+1 < len(videos) and 'long' in videos[i+1]['video_id'] else None
                
                date_str = current_day.strftime("%d/%m/%Y")
                
                if short_vid:
                    # Shorts às 11:30
                    desc = short_vid['legenda_post'] + "\n\n" + short_vid['hashtags']
                    video_path = os.path.abspath(short_vid['caminho_arquivo_video'])
                    upload_video(page, video_path, short_vid['titulo'], desc, date_str, "11:30")
                    time.sleep(5)
                    
                if long_vid:
                    # Longos às 19:00
                    desc = long_vid['legenda_post'] + "\n\n" + long_vid['hashtags']
                    video_path = os.path.abspath(long_vid['caminho_arquivo_video'])
                    upload_video(page, video_path, long_vid['titulo'], desc, date_str, "19:00")
                    time.sleep(5)
                
                current_day += timedelta(days=1)
                
            print("🎉 Todos os vídeos foram agendados!")
            page.close()
            
        except Exception as e:
            print(f"Erro crítico no bot: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python bot_uploader.py <caminho_do_csv>")
        sys.exit(1)
        
    run_bot(sys.argv[1])
