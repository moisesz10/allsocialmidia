import os
from src.interfaces import IScriptGenerator, IAudioGenerator, IVideoComposer


class VideoFactory:
    """Orquestrador do processo de criação de vídeos."""

    def __init__(
        self,
        script_gen: IScriptGenerator,
        audio_gen: IAudioGenerator,
        video_comp: IVideoComposer,
    ):
        self.script_gen = script_gen
        self.audio_gen = audio_gen
        self.video_comp = video_comp

    def run_pipeline(self) -> None:
        print("=== Gerador de Vídeos Faceless ===")

        # 1. Gerar Conteúdo
        text = self.script_gen.generate()
        print(f"\n[Texto Gerado]\n{text}\n")

        # 2. Gerar Áudio e Legendas
        audio_path = "output/temp_audio.mp3"
        srt_path = "output/temp_subs.srt"
        os.makedirs("output", exist_ok=True)

        self.audio_gen.generate_audio_and_subs(text, audio_path, srt_path)

        # 3. Compor o Vídeo
        bg_folder = "assets/backgrounds"
        output_video = "output/final_video.mp4"

        self.video_comp.compose(audio_path, srt_path, bg_folder, output_video)

        # Limpeza
        self._cleanup([audio_path, srt_path])

        print("\nProcesso concluído! Seu vídeo está na pasta 'output/'.")

    def _cleanup(self, files: list[str]) -> None:
        for file in files:
            if os.path.exists(file):
                os.remove(file)
