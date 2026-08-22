import asyncio
import os
from typing import List

import edge_tts
from moviepy.editor import AudioFileClip

from src.interfaces import IAudioGenerator
from src.models import AudioResult, WordTiming

AVAILABLE_VOICES = {
    "pt-BR-AntonioNeural": "Antonio (PT-BR, Profundo & Sério)",
    "pt-BR-FranciscaNeural": "Francisca (PT-BR, Clara & Envolvente)",
    "pt-BR-ThalitaNeural": "Thalita (PT-BR, Jovem & Dinâmica)",
    "pt-BR-NicolauNeural": "Nicolau (PT-BR, Narrador Clássico)",
    "pt-BR-ValerioNeural": "Valério (PT-BR, Enérgico)",
    "en-US-ChristopherNeural": "Christopher (EN-US, Masculino)",
    "en-US-JennyNeural": "Jenny (EN-US, Feminino)",
    "es-ES-AlvaroNeural": "Alvaro (ES-ES, Masculino)",
}


class EdgeTTSAudioGenerator(IAudioGenerator):
    """Gerador de áudio neural de alta qualidade com extração de minutagem por palavra."""

    def __init__(self, default_voice: str = "pt-BR-AntonioNeural"):
        self.default_voice = default_voice

    def generate(
        self,
        text: str,
        voice: str = "pt-BR-AntonioNeural",
        rate: str = "+5%",
        pitch: str = "+0Hz",
        output_audio: str = "output/temp_audio.mp3",
        output_subs: str = "output/temp_subs.srt",
    ) -> AudioResult:
        """Gera o áudio, salva o arquivo e extrai a minutagem de cada palavra."""
        chosen_voice = voice or self.default_voice
        os.makedirs(os.path.dirname(output_audio) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(output_subs) or ".", exist_ok=True)

        words_timing = asyncio.run(
            self._generate_speech_async(
                text=text,
                voice=chosen_voice,
                rate=rate,
                pitch=pitch,
                audio_path=output_audio,
                srt_path=output_subs,
            )
        )

        duration = 0.0
        if os.path.exists(output_audio):
            try:
                clip = AudioFileClip(output_audio)
                duration = float(clip.duration)
                clip.close()
            except Exception:
                if words_timing:
                    duration = words_timing[-1].end + 0.3

        # Se não capturou nenhuma palavra ou a duração for maior que as palavras
        if not words_timing and duration > 0:
            words_timing = self._estimate_word_timings(text, 0.0, duration)

        return AudioResult(
            audio_path=output_audio,
            srt_path=output_subs,
            duration=duration,
            words=words_timing,
        )

    async def _generate_speech_async(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        audio_path: str,
        srt_path: str,
    ) -> List[WordTiming]:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        submaker = edge_tts.SubMaker()
        words_timing: List[WordTiming] = []

        with open(audio_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    try:
                        submaker.feed(chunk)
                    except Exception:
                        pass

                    start_sec = chunk["offset"] / 10_000_000.0
                    duration_sec = chunk["duration"] / 10_000_000.0

                    if chunk["type"] == "WordBoundary":
                        clean_word = chunk["text"].strip()
                        if clean_word:
                            words_timing.append(
                                WordTiming(
                                    word=clean_word,
                                    start=start_sec,
                                    end=start_sec + duration_sec,
                                )
                            )
                    elif chunk["type"] == "SentenceBoundary":
                        sentence_words = self._estimate_word_timings(chunk["text"], start_sec, duration_sec)
                        words_timing.extend(sentence_words)

        # Salva o arquivo SRT gerado pelo edge-tts
        try:
            srt_content = submaker.get_srt()
            with open(srt_path, "w", encoding="utf-8") as srt_file:
                srt_file.write(srt_content)
        except Exception:
            pass

        return words_timing

    def _estimate_word_timings(self, text: str, start_sec: float, duration_sec: float) -> List[WordTiming]:
        """Interpola a minutagem de cada palavra dentro de uma frase falada proporcionalmente ao tamanho."""
        raw_words = text.strip().split()
        if not raw_words or duration_sec <= 0:
            return []

        total_chars = sum(max(1, len(w)) for w in raw_words)
        words: List[WordTiming] = []
        current_time = start_sec

        for word in raw_words:
            word_duration = (max(1, len(word)) / total_chars) * duration_sec
            words.append(
                WordTiming(
                    word=word,
                    start=round(current_time, 3),
                    end=round(current_time + word_duration, 3),
                )
            )
            current_time += word_duration

        return words
