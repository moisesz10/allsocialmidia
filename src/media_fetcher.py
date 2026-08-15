import logging
import os
import random
from typing import List, Optional
import requests
import numpy as np

from src.interfaces import IMediaFetcher

logger = logging.getLogger(__name__)


class SmartMediaFetcher(IMediaFetcher):
    """Buscador inteligente de B-Roll via Pexels API e biblioteca local com fallbacks automáticos."""

    def __init__(
        self,
        pexels_api_key: Optional[str] = None,
        local_dir: str = "assets/backgrounds",
    ):
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY")
        self.local_dir = local_dir
        self.cache_dir = os.path.join(local_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_backgrounds(
        self,
        keywords: List[str],
        count: int = 2,
        orientation: str = "portrait",
    ) -> List[str]:
        """Busca vídeos no Pexels se a chave existir; caso contrário, usa vídeos locais ou gera fundos dinâmicos."""
        selected_files: List[str] = []

        # 1. Tentar buscar via Pexels API se configurada
        if self.pexels_api_key and self.pexels_api_key != "sua_chave_pexels_aqui":
            try:
                for kw in keywords[:count]:
                    fetched = self._search_and_download_pexels(kw, orientation)
                    if fetched:
                        selected_files.append(fetched)
            except Exception as err:
                logger.warning(f"Erro ao buscar no Pexels: {err}")

        # 2. Se não encontrou o suficiente via API, pegar da biblioteca local
        if len(selected_files) < count:
            local_files = self._get_local_files()
            if local_files:
                random.shuffle(local_files)
                for f in local_files:
                    if f not in selected_files:
                        selected_files.append(f)
                    if len(selected_files) >= count:
                        break

        # 3. Se ainda assim não houver nenhum arquivo, gerar um fundo procedural cinematográfico
        if not selected_files:
            procedural = self._generate_procedural_background()
            selected_files.append(procedural)

        return selected_files

    def _search_and_download_pexels(self, query: str, orientation: str) -> Optional[str]:
        headers = {"Authorization": self.pexels_api_key}
        url = "https://api.pexels.com/videos/search"
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": 5,
            "size": "medium",
        }

        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            return None

        data = resp.json()
        videos = data.get("videos", [])
        if not videos:
            return None

        # Escolhe um vídeo da lista
        chosen = random.choice(videos)
        video_files = chosen.get("video_files", [])

        # Procura por resolução adequada (HD 720p ou 1080p)
        best_file = None
        for vf in video_files:
            if vf.get("quality") == "hd" or (vf.get("width", 0) >= 720):
                best_file = vf
                break
        if not best_file and video_files:
            best_file = video_files[0]

        if not best_file:
            return None

        link = best_file.get("link")
        video_id = chosen.get("id")
        file_path = os.path.join(self.cache_dir, f"pexels_{video_id}.mp4")

        if os.path.exists(file_path):
            return file_path

        # Baixar o clipe
        logger.info(f"Baixando B-Roll do Pexels: '{query}'...")
        r = requests.get(link, stream=True, timeout=20)
        if r.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            return file_path

        return None

    def _get_local_files(self) -> List[str]:
        valid_exts = (".mp4", ".mov", ".mkv", ".avi")
        files = []
        for root, _, filenames in os.walk(self.local_dir):
            for name in filenames:
                if name.lower().endswith(valid_exts):
                    files.append(os.path.join(root, name))
        return files

    def _generate_procedural_background(self) -> str:
        """Gera um clipe de fundo dinâmico e cinematográfico com gradiente de partículas se nenhum vídeo existir."""
        output_file = os.path.join(self.cache_dir, "procedural_dark_bg.mp4")
        if os.path.exists(output_file):
            return output_file

        from moviepy.editor import VideoClip

        def make_frame(t):
            # Cria um gradiente escuro dinâmico em movimento
            h, w = 1920, 1080
            y = np.linspace(0, 1, h)[:, None]
            x = np.linspace(0, 1, w)[None, :]

            # Cores suaves e profundas (tons de carvão, azul marinho e vinho)
            r = 15 + 15 * np.sin(y * 3 + t * 0.4)
            g = 18 + 12 * np.cos(x * 2 + t * 0.3)
            b = 28 + 20 * np.sin((x + y) * 2 + t * 0.5)

            frame = np.zeros((h, w, 3), dtype=np.uint8)
            frame[:, :, 0] = np.clip(r, 0, 255).astype(np.uint8)
            frame[:, :, 1] = np.clip(g, 0, 255).astype(np.uint8)
            frame[:, :, 2] = np.clip(b, 0, 255).astype(np.uint8)
            return frame

        clip = VideoClip(make_frame, duration=15.0)
        clip.write_videofile(
            output_file,
            fps=24,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None,
        )
        return output_file
