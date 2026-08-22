from abc import ABC, abstractmethod
from typing import List, Optional
from src.models import YouTubeContentPackage, ScriptResult, AudioResult, VideoConfig


class IScriptGenerator(ABC):
    """Interface para geradores de roteiro com IA."""

    @abstractmethod
    def generate(
        self,
        niche: str = "stoic_philosophy",
        topic: Optional[str] = None,
        language: str = "pt-BR",
    ) -> YouTubeContentPackage:
        """Gera roteiros estruturados (Short e Longo) com hook, corpo, CTA e metadados."""
        pass


class IAudioGenerator(ABC):
    """Interface para geradores de áudio TTS e extração de minutagem."""

    @abstractmethod
    def generate(
        self,
        text: str,
        voice: str = "pt-BR-AntonioNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        output_audio: str = "output/temp_audio.mp3",
        output_subs: str = "output/temp_subs.srt",
    ) -> AudioResult:
        """Gera o arquivo de áudio e extrai os tempos precisos de cada palavra."""
        pass


class IMediaFetcher(ABC):
    """Interface para busca e download de vídeos de apoio (B-Roll)."""

    @abstractmethod
    def fetch_backgrounds(
        self,
        keywords: List[str],
        count: int = 3,
        orientation: str = "portrait",
    ) -> List[str]:
        """Obtém caminhos de arquivos de vídeo de fundo para a composição."""
        pass


class IVideoComposer(ABC):
    """Interface para o compositor visual e renderizador final."""

    @abstractmethod
    def compose(
        self,
        script: ScriptResult,
        audio: AudioResult,
        bg_files: List[str],
        config: VideoConfig,
        output_path: str,
    ) -> str:
        """Composita vídeo, trilha sonora com ducking e legendas dinâmicas."""
        pass
