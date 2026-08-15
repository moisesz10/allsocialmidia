import csv
import json
import os
import time
from datetime import datetime
from typing import Callable, List, Optional

from src.interfaces import IAudioGenerator, IMediaFetcher, IScriptGenerator, IVideoComposer
from src.models import AudioResult, ProductionJobResult, ScriptResult, VideoConfig


class SocialMediaVideoStudio:
    """Orquestrador principal e Estúdio de Produção de Vídeos para Mídias Sociais."""

    def __init__(
        self,
        script_gen: IScriptGenerator,
        audio_gen: IAudioGenerator,
        media_fetcher: IMediaFetcher,
        video_comp: IVideoComposer,
    ):
        self.script_gen = script_gen
        self.audio_gen = audio_gen
        self.media_fetcher = media_fetcher
        self.video_comp = video_comp

    def produce_single_video(
        self,
        niche: str = "stoic_philosophy",
        topic: Optional[str] = None,
        voice: str = "pt-BR-AntonioNeural",
        voice_rate: str = "+5%",
        config: Optional[VideoConfig] = None,
        output_dir: str = "output",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> ProductionJobResult:
        """Executa o pipeline completo de produção de um único vídeo com empacotamento de metadados."""
        def notify(stage: str, percent: int):
            if progress_callback:
                progress_callback(stage, percent)
            print(f"[{percent}%] {stage}")

        config = config or VideoConfig()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_folder = os.path.join(output_dir, f"video_{timestamp}")
        os.makedirs(video_folder, exist_ok=True)

        # 1. Geração de Conteúdo e Roteiro
        notify("Gerando roteiro estratégico com IA...", 15)
        script: ScriptResult = self.script_gen.generate(niche=niche, topic=topic)
        print(f"\n💡 [Título Gerado]: {script.title}")
        print(f"🪝 [Gancho]: {script.hook}")
        print(f"📄 [Texto Completo]:\n{script.full_text}\n")

        # 2. Geração de Voz Neural e Minutagem de Palavras
        notify("Gerando locução neural e minutagem de legendas...", 35)
        audio_path = os.path.join(video_folder, "narration.mp3")
        srt_path = os.path.join(video_folder, "subtitles.srt")
        audio_result: AudioResult = self.audio_gen.generate(
            text=script.full_text,
            voice=voice,
            rate=voice_rate,
            output_audio=audio_path,
            output_subs=srt_path,
        )

        # 3. Busca de B-Roll / Vídeos de Apoio
        notify("Buscando e preparando vídeos de fundo (B-Roll)...", 55)
        orientation = "landscape" if config.aspect_ratio == "16:9" else "portrait"
        bg_files = self.media_fetcher.fetch_backgrounds(
            keywords=script.b_roll_keywords,
            count=3,
            orientation=orientation,
        )

        # 4. Composição e Renderização Final do Vídeo
        notify("Compositando vídeo, áudio ducking e legendas Hormozi...", 75)
        final_video_path = os.path.join(video_folder, "final_video.mp4")
        self.video_comp.compose(
            script=script,
            audio=audio_result,
            bg_files=bg_files,
            config=config,
            output_path=final_video_path,
        )

        # 5. Empacotamento de Metadados para Publicação
        notify("Empacotando metadados e kit de publicação...", 90)
        metadata_path = os.path.join(video_folder, "post_metadata.json")
        copy_path = os.path.join(video_folder, "social_copy.txt")

        metadata_dict = {
            "title": script.title,
            "niche": script.niche,
            "topic": script.topic,
            "hook": script.hook,
            "body": script.body,
            "cta": script.cta,
            "full_text": script.full_text,
            "description": script.description,
            "hashtags": script.hashtags,
            "duration_seconds": round(audio_result.duration, 2),
            "voice": voice,
            "bgm_track": config.bgm_track,
            "aspect_ratio": config.aspect_ratio,
            "created_at": datetime.now().isoformat(),
            "files": {
                "video": "final_video.mp4",
                "audio": "narration.mp3",
                "subtitles": "subtitles.srt",
            },
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, ensure_ascii=False, indent=2)

        # Arquivo de texto pronto para copiar e colar nas redes
        hashtags_str = " ".join(script.hashtags)
        copy_content = (
            f"📌 TÍTULO DO VÍDEO:\n{script.title}\n\n"
            f"📝 LEGENDA / COPY:\n{script.description}\n\n"
            f"🏷️ HASHTAGS:\n{hashtags_str}\n\n"
            f"--------------------------------------------------\n"
            f"🎙️ Roteiro Narrado:\n{script.full_text}\n"
        )
        with open(copy_path, "w", encoding="utf-8") as f:
            f.write(copy_content)

        notify("Produção finalizada com sucesso!", 100)

        return ProductionJobResult(
            video_path=final_video_path,
            script=script,
            duration=audio_result.duration,
            metadata_path=metadata_path,
        )

    def produce_batch(
        self,
        count: int = 3,
        niche: str = "stoic_philosophy",
        custom_topics: Optional[List[str]] = None,
        voice: str = "pt-BR-AntonioNeural",
        voice_rate: str = "+5%",
        config: Optional[VideoConfig] = None,
        output_dir: str = "output",
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[ProductionJobResult]:
        """Gera uma esteira de múltiplos vídeos em lote e cria planilha/cronograma consolidado."""
        batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = os.path.join(output_dir, f"batch_{batch_timestamp}")
        os.makedirs(batch_dir, exist_ok=True)

        results: List[ProductionJobResult] = []
        csv_rows = []

        print("\n=======================================================")
        print(f"🏭 INICIANDO ESTEIRA DE PRODUÇÃO EM LOTE: {count} VÍDEOS")
        print(f"📁 Pasta de destino: {batch_dir}")
        print("=======================================================\n")

        for i in range(count):
            print(f"\n▶️ [Vídeo {i + 1}/{count}] Produzindo...")
            if progress_callback:
                progress_callback(i + 1, count, f"Iniciando vídeo {i + 1}/{count}")

            topic = None
            if custom_topics and i < len(custom_topics):
                topic = custom_topics[i]

            result = self.produce_single_video(
                niche=niche,
                topic=topic,
                voice=voice,
                voice_rate=voice_rate,
                config=config,
                output_dir=batch_dir,
            )
            results.append(result)

            # Adicionar à lista para exportar CSV de agendamento
            csv_rows.append({
                "video_id": f"video_{i + 1:02d}",
                "titulo": result.script.title,
                "nicho": result.script.niche,
                "duracao_segundos": f"{result.duration:.1f}",
                "legenda_post": result.script.description.replace("\n", " "),
                "hashtags": " ".join(result.script.hashtags),
                "caminho_arquivo_video": result.video_path,
            })

            # Pequena pausa entre gerações para evitar throttling
            if i < count - 1:
                time.sleep(1)

        # Gerar CSV de Cronograma / Agendamento para Notion, Metricool, Buffer
        schedule_csv = os.path.join(batch_dir, "cronograma_publicacoes.csv")
        with open(schedule_csv, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "video_id",
                "titulo",
                "nicho",
                "duracao_segundos",
                "legenda_post",
                "hashtags",
                "caminho_arquivo_video",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"\n🎉 Lote de {count} vídeos concluído!")
        print(f"📊 Planilha de agendamento salva em: {schedule_csv}\n")

        return results
