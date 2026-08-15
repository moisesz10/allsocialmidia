import os
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import ImageClip

from src.models import WordTiming, VideoConfig


class HormoziSubtitleRenderer:
    """Renderizador de legendas dinâmicas de alto engajamento (Estilo Hormozi/Viral)."""

    def __init__(self, config: VideoConfig):
        self.config = config
        self.font = self._load_font(config.font_path, config.font_size)

    def _load_font(self, font_path: str, size: int) -> ImageFont.FreeTypeFont:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass

        # Fallbacks de fontes do sistema
        for fallback in [
            "assets/fonts/Anton-Regular.ttf",
            "assets/fonts/Poppins-Bold.ttf",
            "assets/fonts/Montserrat-Variable.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        ]:
            if os.path.exists(fallback):
                try:
                    return ImageFont.truetype(fallback, size)
                except Exception:
                    continue

        return ImageFont.load_default()

    def create_subtitle_clips(
        self, words: List[WordTiming], video_size: Tuple[int, int]
    ) -> List[ImageClip]:
        """Transforma a lista de palavras cronometradas em clips visuais de alta retenção."""
        if not words:
            return []

        width, height = video_size
        chunk_size = max(1, self.config.chunk_size)
        clips: List[ImageClip] = []

        # Agrupa palavras em pedaços de 2 a 3 palavras para ritmo dinâmico
        chunks = [words[i : i + chunk_size] for i in range(0, len(words), chunk_size)]

        for chunk in chunks:
            # Para cada palavra no chunk, gera um frame onde ela está ativa (destacada)
            for idx, active_word in enumerate(chunk):
                word_start = active_word.start
                if idx + 1 < len(chunk):
                    word_end = chunk[idx + 1].start
                else:
                    word_end = active_word.end

                word_duration = max(0.08, word_end - word_start)

                # Gera a imagem PIL com transparência
                img = self._render_chunk_image(
                    chunk=chunk,
                    active_index=idx,
                    canvas_size=(width, int(height * 0.35)),
                )

                # Converte PIL Image para numpy arrays separados (RGB + Máscara Alfa)
                img_np = np.array(img)
                rgb_array = img_np[:, :, :3]
                alpha_array = img_np[:, :, 3] / 255.0

                rgb_clip = ImageClip(rgb_array, ismask=False)
                mask_clip = ImageClip(alpha_array, ismask=True)

                clip = (
                    rgb_clip.set_mask(mask_clip)
                    .set_start(word_start)
                    .set_duration(word_duration)
                    .set_position(("center", int(height * 0.58)))
                )
                clips.append(clip)

        return clips

    def _render_chunk_image(
        self,
        chunk: List[WordTiming],
        active_index: int,
        canvas_size: Tuple[int, int],
    ) -> Image.Image:
        canvas_w, canvas_h = canvas_size
        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Monta os textos e calcula as larguras de cada palavra
        words_text = [w.word.upper() for w in chunk]
        space_bbox = draw.textbbox((0, 0), " ", font=self.font)
        space_width = space_bbox[2] - space_bbox[0]

        word_widths = []
        for w_text in words_text:
            bbox = draw.textbbox((0, 0), w_text, font=self.font)
            word_widths.append(bbox[2] - bbox[0])

        total_width = sum(word_widths) + (len(words_text) - 1) * space_width
        current_x = (canvas_w - total_width) // 2
        y_pos = (canvas_h - (self.font.size if hasattr(self.font, "size") else 60)) // 2

        stroke_w = self.config.stroke_width
        stroke_color = self.config.stroke_color

        for idx, (w_text, w_width) in enumerate(zip(words_text, word_widths)):
            is_active = idx == active_index
            fill_color = self.config.highlight_color if is_active else self.config.text_color

            # Sombra de profundidade
            draw.text(
                (current_x + 4, y_pos + 4),
                w_text,
                font=self.font,
                fill="#000000",
                stroke_width=stroke_w,
                stroke_fill="#000000",
            )

            # Texto principal com contorno de contraste
            draw.text(
                (current_x, y_pos),
                w_text,
                font=self.font,
                fill=fill_color,
                stroke_width=stroke_w,
                stroke_fill=stroke_color,
            )

            current_x += w_width + space_width

        return img
