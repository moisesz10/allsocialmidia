import os
import csv
import json
import textwrap
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageDraw, ImageFont

def get_content():
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = """
Gere conteúdo para o Instagram de um canal focado em Filosofia Estoica ("O Estoico Moderno").
Você precisa gerar 15 itens em formato JSON válido:
- 10 itens devem ser do tipo "post" (imagens com frases). Cada "post" deve ter:
    - "quote": uma citação estoica forte e curta (máximo 15 palavras).
    - "caption": uma legenda engajadora para o post (2-3 parágrafos, com emojis e hashtags).
- 5 itens devem ser do tipo "reel" (vídeos curtos). Cada "reel" deve ter:
    - "caption": uma legenda curta para o vídeo, focada em reter a atenção e gerar comentários (com emojis e hashtags).

Formato esperado (EXATAMENTE isto e mais nada):
[
    {"type": "post", "quote": "...", "caption": "..."},
    ...
    {"type": "reel", "caption": "..."}
]
"""
    print("🧠 Gerando conteúdo com o Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    
    raw_text = response.text
    # Limpa possíveis blocos markdown do json
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
    
    return json.loads(raw_text.strip())

def create_image(text, filename):
    # Cria uma imagem 1080x1080
    img = Image.new('RGB', (1080, 1080), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    font_path = "assets/fonts/Montserrat-Variable.ttf"
    try:
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()
        
    # Quebra de linha
    wrapper = textwrap.TextWrapper(width=25) 
    word_list = wrapper.wrap(text=text) 
    
    # Adiciona aspa no começo
    if word_list:
        word_list[0] = '"' + word_list[0]
        word_list[-1] = word_list[-1] + '"'
        
    text_joined = '\n'.join(word_list)
    
    # Posição centralizada
    bbox = draw.multiline_textbbox((0,0), text_joined, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (1080 - text_width) / 2
    y = (1080 - text_height) / 2
    
    # Sombra
    draw.multiline_text((x+4, y+4), text_joined, font=font, fill=(0,0,0), align="center")
    # Texto
    draw.multiline_text((x, y), text_joined, font=font, fill=(240,240,240), align="center")
    
    # Assinatura
    try:
        font_small = ImageFont.truetype(font_path, 30)
    except:
        font_small = ImageFont.load_default()
    
    sig_text = "@oestoicomoderno"
    s_bbox = draw.textbbox((0,0), sig_text, font=font_small)
    s_w = s_bbox[2] - s_bbox[0]
    draw.text(((1080 - s_w) / 2, 1000), sig_text, font=font_small, fill=(150,150,150))
    
    img.save(filename)

def find_videos():
    # Busca até 5 final_video_short.mp4
    import glob
    videos = []
    # Busca recursiva no output
    for path in glob.glob('output/**/final_video_short.mp4', recursive=True):
        videos.append(os.path.abspath(path))
        if len(videos) >= 5:
            break
    return videos

def main():
    content = get_content()
    
    posts = [c for c in content if c['type'] == 'post']
    reels = [c for c in content if c['type'] == 'reel']
    
    videos = find_videos()
    
    if len(videos) < 5:
        print(f"Aviso: Encontrados apenas {len(videos)} vídeos.")
        
    os.makedirs("output/instagram_batch", exist_ok=True)
    
    csv_file = "data/cronograma_instagram.csv"
    start_date = datetime.now() + timedelta(days=1)
    
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tipo", "data", "hora", "texto", "caminho_midia"])
        
        post_idx = 0
        reel_idx = 0
        
        # 5 dias
        for day in range(5):
            date_str = (start_date + timedelta(days=day)).strftime("%d/%m/%Y")
            
            # 2 Posts
            for time_str in ["10:00 AM", "02:00 PM"]:
                if post_idx < len(posts):
                    p = posts[post_idx]
                    img_name = f"output/instagram_batch/post_{post_idx}.png"
                    create_image(p['quote'], img_name)
                    writer.writerow(["post", date_str, time_str, p['caption'], os.path.abspath(img_name)])
                    post_idx += 1
                    
            # 1 Reel
            if reel_idx < len(reels) and reel_idx < len(videos):
                r = reels[reel_idx]
                writer.writerow(["reel", date_str, "06:00 PM", r['caption'], videos[reel_idx]])
                reel_idx += 1
                
    print(f"✅ Agendamento criado em {csv_file} (Total: {post_idx} posts, {reel_idx} reels)")
    print("Para agendar no Meta Business Suite, basta rodar: node bot_instagram.js")

if __name__ == "__main__":
    main()
