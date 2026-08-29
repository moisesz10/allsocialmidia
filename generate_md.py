import csv
from datetime import datetime, timedelta
import os

csv_file = 'output/batch_20260829_102121/cronograma_publicacoes.csv'
md_file = 'cronograma_manual.md'

amanha = datetime.now() + timedelta(days=1)
current_day = amanha

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = list(csv.DictReader(f))

with open(md_file, 'w', encoding='utf-8') as f:
    f.write("# 📅 Cronograma de Publicações (Upload Manual)\n\n")
    f.write("Aqui estão todos os seus 16 vídeos (8 Shorts e 8 Longos) com os arquivos, títulos e legendas para você copiar e colar no YouTube Studio.\n\n")
    
    for i in range(0, len(reader), 2):
        if i >= len(reader): break
        
        short_vid = reader[i] if 'short' in reader[i]['video_id'] else None
        long_vid = reader[i+1] if i+1 < len(reader) and 'long' in reader[i+1]['video_id'] else None
        
        date_str = current_day.strftime("%d/%m/%Y")
        f.write(f"## 🗓️ {date_str} (Dia {i//2 + 1})\n\n")
        
        if short_vid:
            f.write(f"### 📱 Short (Agendar para 11:30)\n")
            f.write(f"- **Arquivo:** [final_video_short.mp4](file:///home/moises/work/allsocialmidia/{short_vid['caminho_arquivo_video']})\n")
            f.write(f"- **Título:** `{short_vid['titulo']}`\n")
            f.write(f"- **Descrição e Tags:**\n```text\n{short_vid['legenda_post']}\n\n{short_vid['hashtags']}\n```\n\n")
            
        if long_vid:
            f.write(f"### 🖥️ Vídeo Longo (Agendar para 19:00)\n")
            f.write(f"- **Arquivo:** [final_video_long.mp4](file:///home/moises/work/allsocialmidia/{long_vid['caminho_arquivo_video']})\n")
            f.write(f"- **Título:** `{long_vid['titulo']}`\n")
            f.write(f"- **Descrição e Tags:**\n```text\n{long_vid['legenda_post']}\n\n{long_vid['hashtags']}\n```\n\n")
            
        f.write("---\n\n")
        current_day += timedelta(days=1)

print("Gerado com sucesso!")
