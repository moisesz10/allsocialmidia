from abc import ABC, abstractmethod


class IScriptGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        """Gera o texto do roteiro."""
        pass


class IAudioGenerator(ABC):
    @abstractmethod
    def generate_audio_and_subs(
        self, text: str, output_audio: str, output_subs: str
    ) -> None:
        """Gera o arquivo de áudio e de legenda a partir do texto."""
        pass


class IVideoComposer(ABC):
    @abstractmethod
    def compose(
        self, audio_path: str, subs_path: str, bg_folder: str, output_path: str
    ) -> None:
        """Composita e renderiza o vídeo final."""
        pass
