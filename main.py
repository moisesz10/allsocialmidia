import os
import sys
from dotenv import load_dotenv

from src.content import GeminiScriptGenerator
from src.audio import EdgeTTSAudioGenerator
from src.video import MoviePyVideoComposer
from src.orchestrator import VideoFactory


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "sua_chave_api_aqui":
        print("Erro: GEMINI_API_KEY não configurada no arquivo .env.")
        sys.exit(1)

    # Injeção de dependência manual (Composition Root)
    script_gen = GeminiScriptGenerator(api_key=api_key)
    audio_gen = EdgeTTSAudioGenerator(voice="pt-BR-AntonioNeural")
    video_comp = MoviePyVideoComposer()

    # Passa as dependências para a fábrica
    factory = VideoFactory(script_gen, audio_gen, video_comp)
    factory.run_pipeline()


if __name__ == "__main__":
    main()
