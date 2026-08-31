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
Gere conteúdo para o Kwai de um canal focado em Filosofia Estoica ("O Estoico Moderno").
Você precisa gerar 15 itens em formato JSON válido, todos do tipo "short" (vídeos curtos focados para Kwai).
O Kwai valoriza ganchos muito fortes, retenção rápida, e costuma usar hashtags focadas em reflexão, motivação e estoicismo.
Cada "short" deve ter:
    - "caption": uma legenda curta, muito chamativa e persuasiva para o vídeo, focada em reter a atenção e atrair seguidores para o perfil (com emojis e as hashtags adequadas).

Formato esperado (EXATAMENTE isto e mais nada):
[
    {"type": "short", "caption": "..."},
    ...
]
"""
    print("🧠 Gerando conteúdo para Kwai com o Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    
    if not response.text:
        print("❌ Erro: O modelo não retornou texto. O conteúdo pode ter sido bloqueado pelos filtros de segurança.")
        if getattr(response, "candidates", None) and response.candidates:
            print(f"Motivo (finish_reason): {response.candidates[0].finish_reason}")
        return []

    raw_text = response.text
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
    
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON retornado pela API:")
        print(raw_text)
        return []

def find_videos():
    videos = []
    for path in glob.glob('output/**/final_video_short.mp4', recursive=True):
        videos.append(os.path.abspath(path))
        if len(videos) >= 15:
            break
    return videos

def main():
    content = get_content()
    if not content:
        print("Nenhum conteúdo foi gerado. Abortando.")
        return
        
    shorts = [c for c in content if c['type'] == 'short']
    videos = find_videos()
    
    if len(videos) < 15:
        print(f"Aviso: Encontrados apenas {len(videos)} vídeos. Requerido: 15.")
        
    csv_file = "data/cronograma_kwai.csv"
    os.makedirs("data", exist_ok=True)
    start_date = datetime.now()
    
    # Estratégia de melhores horários para postagem diária
    horarios = ["07:00 AM", "12:00 PM", "06:00 PM"]
    
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tipo", "data", "hora", "texto", "caminho_midia"])
        
        short_idx = 0
        for day in range(5):
            date_str = (start_date + timedelta(days=day)).strftime("%d/%m/%Y")
            
            for hora in horarios:
                if short_idx < len(shorts) and short_idx < len(videos):
                    s = shorts[short_idx]
                    writer.writerow(["kwai_short", date_str, hora, s['caption'], videos[short_idx]])
                    short_idx += 1
                
    print(f"✅ Agendamento do Kwai criado em {csv_file} (Total: {short_idx} vídeos gerados de hoje até sexta-feira)")

if __name__ == "__main__":
    main()
