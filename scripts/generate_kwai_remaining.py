import sys
import os

sys.path.append(os.getcwd())

from src.cli import build_studio
from src.models import VideoConfig

topics = [
    "como os estóicos encaravam a perda e o luto",
    "a disciplina inabalável de sêneca",
    "amor fati: o poder de amar o próprio destino",
    "o que o estoicismo ensina sobre o dinheiro e a riqueza",
    "como acordar cedo e vencer a preguiça com marco aurélio"
]

def main():
    studio = build_studio()
    config = VideoConfig(
        aspect_ratio="9:16",
        width=1080,
        height=1920,
        highlight_color="#FFE600",
        bgm_track="dark_stoic"
    )

    print("Iniciando geração dos 5 vídeos restantes para totalizar 10...")
    studio.produce_batch(
        count=5,
        niche="stoic_philosophy",
        custom_topics=topics,
        voice="pt-BR-AntonioNeural",
        config=config
    )
    print("Processo finalizado!")

if __name__ == "__main__":
    main()
