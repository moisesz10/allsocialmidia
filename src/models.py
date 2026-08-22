from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WordTiming:
    """Representa a minutagem de uma palavra individual falada."""
    word: str
    start: float
    end: float


@dataclass
class ScriptResult:
    """Representa o roteiro completo estruturado com metadados para mídias sociais."""
    niche: str
    topic: str
    hook: str
    body: str
    cta: str
    full_text: str
    title: str
    description: str
    video_type: str = "short"  # "short" ou "long"
    hashtags: List[str] = field(default_factory=list)
    b_roll_keywords: List[str] = field(default_factory=list)


@dataclass
class YouTubeContentPackage:
    """Pacote contendo o roteiro do vídeo curto e do vídeo longo."""
    short_script: ScriptResult
    long_script: ScriptResult


@dataclass
class AudioResult:
    """Resultado do processamento de áudio com timestamps precisos."""
    audio_path: str
    srt_path: str
    duration: float
    words: List[WordTiming] = field(default_factory=list)


@dataclass
class VideoConfig:
    """Configurações visuais e sonoras de composição do vídeo."""
    aspect_ratio: str = "9:16"  # "9:16", "16:9", "1:1"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    font_path: str = "assets/fonts/Anton-Regular.ttf"
    font_size: int = 80
    highlight_color: str = "#FFE600"  # Amarelo Neon
    text_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: int = 6
    chunk_size: int = 2  # Quantidade de palavras visíveis por vez
    bgm_track: Optional[str] = "dark_stoic"  # Nome da faixa em assets/music
    bgm_volume: float = 0.15
    darken_opacity: float = 0.45
    zoom_effect: bool = True
    progress_bar: bool = True


@dataclass
class ProductionJobResult:
    """Relatório final de produção de um vídeo."""
    video_path: str
    script: ScriptResult
    duration: float
    metadata_path: str
