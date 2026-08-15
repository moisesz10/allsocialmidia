import asyncio
import edge_tts

from src.interfaces import IAudioGenerator


class EdgeTTSAudioGenerator(IAudioGenerator):
    def __init__(self, voice: str = "pt-BR-AntonioNeural"):
        self.voice = voice

    def generate_audio_and_subs(
        self, text: str, output_audio: str, output_subs: str
    ) -> None:
        print(f"Gerando áudio e legendas com a voz {self.voice}...")
        asyncio.run(self._generate_audio(text, output_audio, output_subs))
        print(f"Áudio salvo em {output_audio}")
        print(f"Legendas salvas em {output_subs}")

    async def _generate_audio(
        self, text: str, output_file: str, subtitle_file: str
    ) -> None:
        communicate = edge_tts.Communicate(text, self.voice)
        submaker = edge_tts.SubMaker()

        with open(output_file, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.create_sub(
                        (chunk["offset"], chunk["duration"]), chunk["text"]
                    )

        with open(subtitle_file, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())
