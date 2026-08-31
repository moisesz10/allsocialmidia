import os
import csv
import json
import glob
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

def get_content():
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = """
Gere conteúdo para o Instagram de um canal focado em Filosofia Estoica ("O Estoico Moderno").
Você precisa gerar 7 itens em formato JSON válido, todos do tipo "reel" (vídeos curtos).
Cada "reel" deve ter:
    - "caption": uma legenda curta para o vídeo, focada em reter a atenção e gerar comentários (com emojis e hashtags).

Formato esperado (EXATAMENTE isto e mais nada):
[
    {"type": "reel", "caption": "..."},
    ...
]
"""
    print("🧠 Gerando conteúdo com o Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    
    raw_text = response.text
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
    
    return json.loads(raw_text.strip())

def find_videos():
    videos = []
    for path in glob.glob('output/**/final_video_short.mp4', recursive=True):
        videos.append(os.path.abspath(path))
        if len(videos) >= 7:
            break
    return videos

def main():
    content = get_content()
    reels = [c for c in content if c['type'] == 'reel']
    videos = find_videos()
    
    if len(videos) < 7:
        print(f"Aviso: Encontrados apenas {len(videos)} vídeos.")
        
    csv_file = "data/cronograma_reels.csv"
    start_date = datetime.now() + timedelta(days=1)
    
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tipo", "data", "hora", "texto", "caminho_midia"])
        
        reel_idx = 0
        for day in range(7):
            date_str = (start_date + timedelta(days=day)).strftime("%d/%m/%Y")
            
            if reel_idx < len(reels) and reel_idx < len(videos):
                r = reels[reel_idx]
                writer.writerow(["reel", date_str, "06:00 PM", r['caption'], videos[reel_idx]])
                reel_idx += 1
                
    print(f"✅ Agendamento de Reels criado em {csv_file} (Total: {reel_idx} reels)")

if __name__ == "__main__":
    main()
