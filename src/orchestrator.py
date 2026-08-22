import csv
import json
import os
import time
from datetime import datetime
from typing import Callable, List, Optional

from src.interfaces import IAudioGenerator, IMediaFetcher, IScriptGenerator, IVideoComposer
from src.models import AudioResult, ProductionJobResult, ScriptResult, VideoConfig, YouTubeContentPackage


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

    def produce_youtube_package(
        self,
        niche: str = "stoic_philosophy",
        topic: Optional[str] = None,
        voice: str = "pt-BR-AntonioNeural",
        voice_rate: str = "+5%",
        config: Optional[VideoConfig] = None,
        output_dir: str = "output",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[ProductionJobResult]:
        """Executa o pipeline completo de produção de um pacote YouTube (Short + Longo)."""
        def notify(stage: str, percent: int):
            if progress_callback:
                progress_callback(stage, percent)
            print(f"[{percent}%] {stage}")

        config = config or VideoConfig()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_folder = os.path.join(output_dir, f"package_{timestamp}")
        os.makedirs(package_folder, exist_ok=True)

        notify("Gerando pacote estratégico de roteiros com IA...", 10)
        package: YouTubeContentPackage = self.script_gen.generate(niche=niche, topic=topic)
        
        results = []
        
        # Helper interno para renderizar cada roteiro
        def process_script(script: ScriptResult, v_type: str, percent_start: int):
            print(f"\n💡 [Título {v_type.upper()}]: {script.title}")
            print(f"🪝 [Gancho]: {script.hook}")
            
            # Ajustando aspect ratio
            current_config = VideoConfig(
                aspect_ratio="9:16" if script.video_type == "short" else "16:9",
                width=1080 if script.video_type == "short" else 1920,
                height=1920 if script.video_type == "short" else 1080,
                highlight_color=config.highlight_color,
                bgm_track=config.bgm_track,
            )

            notify(f"Gerando áudio ({v_type})...", percent_start + 5)
            audio_path = os.path.join(package_folder, f"narration_{v_type}.mp3")
            srt_path = os.path.join(package_folder, f"subtitles_{v_type}.srt")
            audio_result = self.audio_gen.generate(
                text=script.full_text,
                voice=voice,
                rate=voice_rate,
                output_audio=audio_path,
                output_subs=srt_path,
            )

            notify(f"Buscando B-Roll ({v_type})...", percent_start + 15)
            orientation = "landscape" if current_config.aspect_ratio == "16:9" else "portrait"
            bg_files = self.media_fetcher.fetch_backgrounds(
                keywords=script.b_roll_keywords,
                count=3,
                orientation=orientation,
            )

            notify(f"Renderizando vídeo ({v_type})...", percent_start + 25)
            final_video_path = os.path.join(package_folder, f"final_video_{v_type}.mp4")
            self.video_comp.compose(
                script=script,
                audio=audio_result,
                bg_files=bg_files,
                config=current_config,
                output_path=final_video_path,
            )

            notify(f"Empacotando metadados ({v_type})...", percent_start + 35)
            metadata_path = os.path.join(package_folder, f"post_metadata_{v_type}.json")
            copy_path = os.path.join(package_folder, f"social_copy_{v_type}.txt")

            metadata_dict = {
                "title": script.title,
                "niche": script.niche,
                "topic": script.topic,
                "hook": script.hook,
                "full_text": script.full_text,
                "description": script.description,
                "hashtags": script.hashtags,
                "video_type": script.video_type,
                "duration_seconds": round(audio_result.duration, 2),
                "voice": voice,
                "aspect_ratio": current_config.aspect_ratio,
            }

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, ensure_ascii=False, indent=2)

            with open(copy_path, "w", encoding="utf-8") as f:
                f.write(f"📌 TÍTULO:\n{script.title}\n\n📝 COPY:\n{script.description}\n\n🎙️ TEXTO:\n{script.full_text}\n")

            return ProductionJobResult(
                video_path=final_video_path,
                script=script,
                duration=audio_result.duration,
                metadata_path=metadata_path,
            )

        # Processar os dois
        short_result = process_script(package.short_script, "short", 10)
        long_result = process_script(package.long_script, "long", 50)
        
        results.extend([short_result, long_result])
        notify("Pacote YouTube finalizado com sucesso!", 100)
        return results

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

            package_results = self.produce_youtube_package(
                niche=niche,
                topic=topic,
                voice=voice,
                voice_rate=voice_rate,
                config=config,
                output_dir=batch_dir,
            )
            results.extend(package_results)

            for result in package_results:
                # Adicionar à lista para exportar CSV de agendamento
                csv_rows.append({
                    "video_id": f"video_{i + 1:02d}_{result.script.video_type}",
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
