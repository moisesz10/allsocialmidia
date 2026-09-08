import sys
import os

# Adiciona o diretório atual ao path para importações
sys.path.append(os.getcwd())

from src.cli import build_studio
from src.models import VideoConfig

topics = [
    "como lidar com a rejeição segundo os estóicos",
    "o segredo de marco aurélio para não se importar com a opinião alheia",
    "a técnica estóica para vencer a ansiedade",
    "por que você deve abraçar o desconforto",
    "a arte de não reagir e manter a calma",
    "como os estóicos encaravam a perda e o luto",
    "a disciplina inabalável de sêneca",
    "amor fati: o poder de amar o próprio destino",
    "o que o estoicismo ensina sobre o dinheiro e a riqueza",
    "como acordar cedo e vencer a preguiça com marco aurélio",
    "a visão estóica sobre a traição e a decepção",
    "memento mori: por que lembrar da morte te faz viver melhor",
    "como lidar com pessoas tóxicas usando a razão",
    "o verdadeiro significado de controle emocional",
    "como dominar a raiva antes que ela te domine",
    "a verdadeira liberdade segundo epicteto",
    "como os estóicos encontravam a felicidade no mínimo",
    "o poder da visualização negativa",
    "como transformar obstáculos em oportunidades",
    "a sabedoria estóica para tomar decisões difíceis"
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

    print("Iniciando geração de 20 vídeos para o Kwai...")
    studio.produce_batch(
        count=20,
        niche="stoic_philosophy",
        custom_topics=topics,
        voice="pt-BR-AntonioNeural",
        config=config
    )
    print("Processo finalizado!")

if __name__ == "__main__":
    main()
