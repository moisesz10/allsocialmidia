import os
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from google.genai import types

def generate_posts():
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = """
Você é um estrategista de conteúdo focado em Filosofia Estoica para o YouTube.
Escreva exatamente 20 postagens curtas e engajadoras para a aba "Comunidade" de um canal no YouTube chamado "O Estoico Moderno".
Cada postagem deve:
- Ter 2 a 4 parágrafos curtos.
- Incluir emojis relevantes.
- Terminar com uma pergunta reflexiva para os inscritos comentarem.
- Ser independente das outras (cada uma explora um aspecto diferente: resiliência, silêncio, memento mori, amor fati, etc).

Formato da resposta: Separe cada postagem com a string exata "---POST_SEPARATOR---"
Não adicione títulos ou numeração no início de cada post, apenas o texto da postagem.
"""
    print("🧠 Gerando 20 postagens com o Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    
    posts_text = response.text.split("---POST_SEPARATOR---")
    posts = [p.strip() for p in posts_text if p.strip()]
    
    # Limita a 20 postagens caso gere mais
    posts = posts[:20]
    
    print(f"✅ Foram geradas {len(posts)} postagens.")
    
    # Salva no CSV
    csv_file = "cronograma_comunidade.csv"
    current_day = datetime.now()
    
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["data", "hora", "texto"])
        
        for i in range(0, len(posts), 2):
            post1 = posts[i]
            post2 = posts[i+1] if i+1 < len(posts) else None
            
            date_str = current_day.strftime("%d/%m/%Y")
            
            writer.writerow([date_str, "11:30", post1])
            if post2:
                writer.writerow([date_str, "19:00", post2])
                
            current_day += timedelta(days=1)
            
    print(f"📁 Planilha de agendamento da comunidade salva em {csv_file}")

if __name__ == "__main__":
    generate_posts()
