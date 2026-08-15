import os
import random
import re
from typing import List, Dict, Any
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
)

from src.interfaces import IVideoComposer


def parse_srt(srt_file: str) -> List[Dict[str, Any]]:
    """Extrai tempos e palavras de um arquivo SRT."""
    subs = []
    with open(srt_file, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            time_line = lines[1]
            text_line = " ".join(lines[2:])
            m = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3})\s-->\s(\d{2}:\d{2}:\d{2},\d{3})", time_line
            )
            if m:
                start_str, end_str = m.groups()
                start_time = _time_to_sec(start_str)
                end_time = _time_to_sec(end_str)
                subs.append(
                    {"start": start_time, "end": end_time, "text": text_line.strip()}
                )
    return subs


def _time_to_sec(t_str: str) -> float:
    """Converte tempo SRT (HH:MM:SS,MMM) para segundos."""
    h, m, s = t_str.split(":")
    s, ms = s.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


class MoviePyVideoComposer(IVideoComposer):
    def compose(
        self, audio_path: str, subs_path: str, bg_folder: str, output_path: str
    ) -> None:
        print("Iniciando composição do vídeo...")
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration

        bg_clip = self._get_background_clip(bg_folder, audio_duration)

        text_clips = self._create_text_clips(subs_path, bg_clip.size)

        final_video = CompositeVideoClip([bg_clip] + text_clips)
        final_video = final_video.set_audio(audio_clip)

        print(f"Renderizando vídeo final em {output_path}...")
        final_video.write_videofile(
            output_path, fps=30, codec="libx264", audio_codec="aac"
        )
        print("Vídeo renderizado com sucesso!")

    def _get_background_clip(
        self, bg_folder: str, duration: float
    ) -> VideoFileClip | ColorClip:
        bg_files = []
        if os.path.exists(bg_folder):
            bg_files = [
                os.path.join(bg_folder, f)
                for f in os.listdir(bg_folder)
                if f.endswith((".mp4", ".mov"))
            ]

        if bg_files:
            bg_file = random.choice(bg_files)
            bg_clip = VideoFileClip(bg_file)

            if bg_clip.duration < duration:
                from moviepy.video.fx.all import loop

                bg_clip = loop(bg_clip, duration=duration)
            else:
                bg_clip = bg_clip.subclip(0, duration)

            darken_clip = (
                ColorClip(size=bg_clip.size, color=(0, 0, 0))
                .set_opacity(0.4)
                .set_duration(duration)
            )
            return CompositeVideoClip([bg_clip, darken_clip])

        print("Nenhum vídeo de fundo encontrado, usando fundo sólido.")
        return ColorClip(size=(1080, 1920), color=(30, 30, 30)).set_duration(duration)

    def _create_text_clips(self, subs_path: str, video_size: tuple) -> List[TextClip]:
        subs = parse_srt(subs_path)
        text_clips = []

        for sub in subs:
            txt_clip = TextClip(
                sub["text"],
                fontsize=90,
                color="white",
                font="Arial-Bold",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(video_size[0] * 0.8, None),
                align="center",
            )
            txt_clip = txt_clip.set_start(sub["start"]).set_end(sub["end"])
            txt_clip = txt_clip.set_position(("center", "center"))
            text_clips.append(txt_clip)

        return text_clips
