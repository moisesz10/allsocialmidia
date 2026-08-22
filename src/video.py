import os
import random
from typing import List, Optional, Tuple

import PIL.Image

# Compatibilidade Pillow 10+ com MoviePy 1.0.3
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips,
)

from src.interfaces import IVideoComposer
from src.models import AudioResult, ScriptResult, VideoConfig
from src.subtitles import HormoziSubtitleRenderer


class MoviePyVideoComposer(IVideoComposer):
    """Compositor de vídeo avançado com suporte a B-Roll dinâmico, legendas Hormozi e BGM Ducking."""

    def compose(
        self,
        script: ScriptResult,
        audio: AudioResult,
        bg_files: List[str],
        config: VideoConfig,
        output_path: str,
    ) -> str:
        """Renderiza o vídeo final unindo mídia de apoio, locução, trilha sonora e legendas."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        total_duration = audio.duration

        print(f"🎬 Iniciando composição do vídeo ({config.aspect_ratio} - {total_duration:.1f}s)...")

        # 1. Preparar o clipe de fundo (B-Roll cortado ou em loop)
        bg_clip = self._prepare_background(
            bg_files=bg_files,
            target_duration=total_duration,
            target_size=(config.width, config.height),
            darken_opacity=config.darken_opacity,
        )

        # 2. Renderizar camadas de legendas dinâmicas estilo Hormozi
        subtitle_renderer = HormoziSubtitleRenderer(config)
        subtitle_clips = subtitle_renderer.create_subtitle_clips(
            words=audio.words,
            video_size=(config.width, config.height),
        )

        # 3. Barra de progresso inferior (se habilitada)
        extra_clips = []
        if config.progress_bar:
            progress_clip = self._create_progress_bar(
                duration=total_duration,
                width=config.width,
                height=config.height,
                color=config.highlight_color,
            )
            extra_clips.append(progress_clip)

        # 4. Compositar todas as camadas visuais
        all_visual_clips = [bg_clip] + extra_clips + subtitle_clips
        final_video = CompositeVideoClip(
            all_visual_clips,
            size=(config.width, config.height),
        ).set_duration(total_duration)

        # 5. Mixagem de áudio (Locução + Trilha Sonora com Ducking)
        final_audio = self._mix_audio(
            voice_audio_path=audio.audio_path,
            total_duration=total_duration,
            bgm_name=config.bgm_track,
            bgm_volume=config.bgm_volume,
        )
        final_video = final_video.set_audio(final_audio)

        # 6. Renderizar arquivo final em disco
        print(f"🚀 Renderizando arquivo final em {output_path}...")
        final_video.write_videofile(
            output_path,
            fps=config.fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="fast",
            logger=None,
        )

        # Fechar clips para liberar recursos de memória
        try:
            final_video.close()
            final_audio.close()
        except Exception:
            pass

        print(f"✅ Vídeo gerado com sucesso: {output_path}")
        return output_path

    def _prepare_background(
        self,
        bg_files: List[str],
        target_duration: float,
        target_size: Tuple[int, int],
        darken_opacity: float,
    ) -> CompositeVideoClip:
        target_w, target_h = target_size
        valid_files = [f for f in bg_files if os.path.exists(f)]

        if not valid_files:
            base_clip = ColorClip(size=target_size, color=(20, 20, 25)).set_duration(target_duration)
            return base_clip

        # Se houver múltiplos arquivos de B-Roll, faz cortes a cada 4-6 segundos
        clip_segments = []
        segment_duration = 5.0
        remaining = target_duration
        file_idx = 0

        while remaining > 0:
            dur = min(segment_duration, remaining)
            fpath = valid_files[file_idx % len(valid_files)]
            file_idx += 1

            raw_clip = VideoFileClip(fpath)
            # Corta um trecho aleatório ou inicial
            start_t = 0.0
            if raw_clip.duration > dur + 1.0:
                start_t = random.uniform(0, max(0.1, raw_clip.duration - dur - 0.5))

            sub = raw_clip.subclip(start_t, start_t + dur)
            scaled = self._crop_and_resize(sub, target_w, target_h)
            clip_segments.append(scaled)
            remaining -= dur

        if len(clip_segments) == 1:
            bg_video = clip_segments[0]
        else:
            bg_video = concatenate_videoclips(clip_segments, method="compose")

        bg_video = bg_video.set_duration(target_duration)

        # Camada escura de contraste para leitura de legendas
        dark_overlay = (
            ColorClip(size=target_size, color=(0, 0, 0)).set_opacity(darken_opacity).set_duration(target_duration)
        )

        return CompositeVideoClip([bg_video, dark_overlay])

    def _crop_and_resize(self, clip: VideoFileClip, target_w: int, target_h: int) -> VideoFileClip:
        w, h = clip.size
        target_ratio = target_w / target_h
        current_ratio = w / h

        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            x_center = w / 2
            clip = clip.crop(x1=int(x_center - new_w / 2), width=new_w, y1=0, height=h)
        else:
            new_h = int(w / target_ratio)
            y_center = h / 2
            clip = clip.crop(x1=0, width=w, y1=int(y_center - new_h / 2), height=new_h)

        return clip.resize((target_w, target_h))

    def _mix_audio(
        self,
        voice_audio_path: str,
        total_duration: float,
        bgm_name: Optional[str],
        bgm_volume: float,
    ) -> CompositeAudioClip:
        voice_clip = AudioFileClip(voice_audio_path)

        bgm_clip = None
        if bgm_name:
            possible_paths = [
                os.path.join("assets/music", f"{bgm_name}.wav"),
                os.path.join("assets/music", f"{bgm_name}.mp3"),
                os.path.join("assets/music", bgm_name),
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    try:
                        raw_bgm = AudioFileClip(p)
                        if raw_bgm.duration < total_duration:
                            from moviepy.audio.fx.all import audio_loop

                            raw_bgm = audio_loop(raw_bgm, duration=total_duration)
                        else:
                            raw_bgm = raw_bgm.subclip(0, total_duration)

                        bgm_clip = raw_bgm.volumex(bgm_volume)
                        break
                    except Exception as e:
                        print(f"Aviso ao carregar música {bgm_name}: {e}")
                        break

        if bgm_clip:
            return CompositeAudioClip([bgm_clip, voice_clip]).set_duration(total_duration)
        return voice_clip

    def _create_progress_bar(self, duration: float, width: int, height: int, color: str):
        """Cria uma barra de progresso horizontal fina no rodapé do vídeo."""
        import numpy as np
        from moviepy.editor import VideoClip

        hex_val = color.lstrip("#")
        rgb = tuple(int(hex_val[i : i + 2], 16) for i in (0, 2, 4))
        bar_h = 6

        def make_frame(t):
            progress = min(1.0, max(0.0, t / duration))
            current_w = max(1, int(width * progress))
            frame = np.zeros((bar_h, width, 3), dtype=np.uint8)
            frame[:, :current_w, :] = rgb
            return frame

        return VideoClip(make_frame, duration=duration).set_position((0, height - bar_h)).set_duration(duration)
