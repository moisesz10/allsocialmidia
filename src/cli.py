import argparse
import os
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from src.audio import AVAILABLE_VOICES, EdgeTTSAudioGenerator
from src.content import NICHE_PROMPTS, GeminiScriptGenerator
from src.media_fetcher import SmartMediaFetcher
from src.models import VideoConfig
from src.orchestrator import SocialMediaVideoStudio
from src.video import MoviePyVideoComposer

console = Console()


def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]🎬 ALLSOCIALMIDIA[/bold cyan] - [bold magenta]Produtora Automatizada de Vídeos para Redes Sociais[/bold magenta]\n"
            "[dim]Geração de Roteiros Virais • Vozes Neurais • B-Roll Inteligente • Legendas Hormozi • Ducking de Áudio[/dim]",
            border_style="bright_blue",
        )
    )


def interactive_mode(studio: SocialMediaVideoStudio):
    print_banner()

    console.print("\n[bold yellow]🎯 Escolha o Nicho de Conteúdo:[/bold yellow]")
    niches = list(NICHE_PROMPTS.keys())
    for idx, n in enumerate(niches, 1):
        console.print(f"  [cyan]{idx}.[/cyan] {NICHE_PROMPTS[n]['name']} [dim]({n})[/dim]")

    niche_idx = IntPrompt.ask(
        "Selecione o número do nicho",
        default=1,
    )
    chosen_niche = niches[max(0, min(len(niches) - 1, niche_idx - 1))]

    custom_topic = Prompt.ask(
        "\n[bold yellow]📝 Tópico Específico[/bold yellow] (deixe vazio para sugestão automática da IA)",
        default="",
    )
    chosen_topic = custom_topic.strip() or None

    console.print("\n[bold yellow]🎙️ Escolha a Voz da Narração:[/bold yellow]")
    voices = list(AVAILABLE_VOICES.keys())
    for idx, v in enumerate(voices, 1):
        console.print(f"  [cyan]{idx}.[/cyan] {AVAILABLE_VOICES[v]}")

    voice_idx = IntPrompt.ask("Selecione a voz", default=1)
    chosen_voice = voices[max(0, min(len(voices) - 1, voice_idx - 1))]

    console.print("\n[bold yellow]📐 Proporção do Vídeo (Aspect Ratio):[/bold yellow]")
    console.print(
        "  [cyan]1.[/cyan] 9:16 (TikTok, Instagram Reels, YouTube Shorts) [bold green][Recomendado][/bold green]"
    )
    console.print("  [cyan]2.[/cyan] 16:9 (YouTube Widescreen, Twitter/X)")
    console.print("  [cyan]3.[/cyan] 1:1 (Feed Instagram, LinkedIn)")

    ratio_choice = IntPrompt.ask("Selecione o formato", default=1)
    aspect_map = {1: ("9:16", 1080, 1920), 2: ("16:9", 1920, 1080), 3: ("1:1", 1080, 1080)}
    aspect_ratio, width, height = aspect_map.get(ratio_choice, ("9:16", 1080, 1920))

    console.print("\n[bold yellow]🎵 Trilha Sonora de Fundo:[/bold yellow]")
    console.print("  [cyan]1.[/cyan] dark_stoic (Épica, Profunda)")
    console.print("  [cyan]2.[/cyan] ambient_lofi (Chill, Suave)")
    console.print("  [cyan]3.[/cyan] mystery_suspense (Mistério, Tensão)")
    console.print("  [cyan]4.[/cyan] Sem música de fundo")

    bgm_choice = IntPrompt.ask("Selecione a trilha", default=1)
    bgm_map = {1: "dark_stoic", 2: "ambient_lofi", 3: "mystery_suspense", 4: None}
    chosen_bgm = bgm_map.get(bgm_choice, "dark_stoic")

    console.print("\n[bold yellow]🎨 Cor de Destaque das Legendas (Hormozi):[/bold yellow]")
    console.print("  [cyan]1.[/cyan] Amarelo Neon (#FFE600)")
    console.print("  [cyan]2.[/cyan] Verde Neon (#00FF66)")
    console.print("  [cyan]3.[/cyan] Ciano Elétrico (#00F0FF)")
    console.print("  [cyan]4.[/cyan] Rosa Magenta (#FF0055)")

    color_choice = IntPrompt.ask("Selecione a cor", default=1)
    color_map = {1: "#FFE600", 2: "#00FF66", 3: "#00F0FF", 4: "#FF0055"}
    highlight_color = color_map.get(color_choice, "#FFE600")

    count = IntPrompt.ask("\n[bold yellow]🔢 Quantos vídeos deseja produzir?[/bold yellow]", default=1)

    config = VideoConfig(
        aspect_ratio=aspect_ratio,
        width=width,
        height=height,
        highlight_color=highlight_color,
        bgm_track=chosen_bgm,
    )

    console.print("\n[bold green]🚀 Iniciando linha de produção...[/bold green]\n")

    if count == 1:
        results = studio.produce_youtube_package(
            niche=chosen_niche,
            topic=chosen_topic,
            voice=chosen_voice,
            config=config,
        )
        show_result_table(results)
    else:
        results = studio.produce_batch(
            count=count,
            niche=chosen_niche,
            voice=chosen_voice,
            config=config,
        )
        show_result_table(results)


def show_result_table(results):
    table = Table(title="✨ Resumo da Produção", border_style="bright_green")
    table.add_column("Arquivo de Vídeo", style="cyan")
    table.add_column("Título", style="bold white")
    table.add_column("Nicho", style="yellow")
    table.add_column("Duração", style="magenta")

    for r in results:
        table.add_row(
            r.video_path,
            r.script.title,
            r.script.niche,
            f"{r.duration:.1f}s",
        )

    console.print("\n")
    console.print(table)
    console.print(
        "\n[bold green]🎉 Todos os arquivos e kits de publicação estão prontos na pasta output/![/bold green]\n"
    )


def build_studio() -> SocialMediaVideoStudio:
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    pexels_key = os.getenv("PEXELS_API_KEY")

    script_gen = GeminiScriptGenerator(api_key=gemini_key)
    audio_gen = EdgeTTSAudioGenerator()
    media_fetcher = SmartMediaFetcher(pexels_api_key=pexels_key)
    video_comp = MoviePyVideoComposer()

    return SocialMediaVideoStudio(
        script_gen=script_gen,
        audio_gen=audio_gen,
        media_fetcher=media_fetcher,
        video_comp=video_comp,
    )


def run_cli():
    parser = argparse.ArgumentParser(description="AllSocialMidia - Produtora de Vídeos para Redes Sociais")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo menu interativo")
    parser.add_argument("--web", "-w", action="store_true", help="Inicia o Web Studio (Interface Gráfica)")
    parser.add_argument("--port", type=int, default=8000, help="Porta para o Web Studio")
    parser.add_argument("--niche", type=str, default="stoic_philosophy", help="Nicho de conteúdo")
    parser.add_argument("--topic", type=str, default=None, help="Tópico personalizado")
    parser.add_argument("--voice", type=str, default="pt-BR-AntonioNeural", help="Voz Edge-TTS")
    parser.add_argument("--count", type=int, default=1, help="Quantidade de vídeos em lote")
    parser.add_argument("--aspect-ratio", type=str, default="9:16", choices=["9:16", "16:9", "1:1"])
    parser.add_argument("--bgm", type=str, default="dark_stoic", help="Trilha sonora de fundo")
    parser.add_argument("--color", type=str, default="#FFE600", help="Cor de destaque das legendas")

    args = parser.parse_args()

    if args.web:
        from src.web.app import start_web_studio

        start_web_studio(port=args.port)
        return

    studio = build_studio()

    if args.interactive or len(sys.argv) == 1:
        interactive_mode(studio)
        return

    # Modo flags direto
    ratio_res = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
    w, h = ratio_res.get(args.aspect_ratio, (1080, 1920))

    config = VideoConfig(
        aspect_ratio=args.aspect_ratio,
        width=w,
        height=h,
        highlight_color=args.color,
        bgm_track=args.bgm if args.bgm != "none" else None,
    )

    if args.count > 1:
        results = studio.produce_batch(
            count=args.count,
            niche=args.niche,
            custom_topics=[args.topic] if args.topic else None,
            voice=args.voice,
            config=config,
        )
        show_result_table(results)
    else:
        results = studio.produce_youtube_package(
            niche=args.niche,
            topic=args.topic,
            voice=args.voice,
            config=config,
        )
        show_result_table(results)
