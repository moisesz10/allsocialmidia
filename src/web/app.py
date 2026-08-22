import asyncio
import os
import uuid
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.audio import AVAILABLE_VOICES, EdgeTTSAudioGenerator
from src.content import NICHE_PROMPTS, GeminiScriptGenerator
from src.media_fetcher import SmartMediaFetcher
from src.models import ScriptResult, VideoConfig
from src.orchestrator import SocialMediaVideoStudio
from src.video import MoviePyVideoComposer

app = FastAPI(title="AllSocialMidia Web Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output", exist_ok=True)
os.makedirs("assets/music", exist_ok=True)
os.makedirs("assets/backgrounds", exist_ok=True)

app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# In-memory storage for async job tracking
JOBS: Dict[str, Dict[str, Any]] = {}


class GenerateScriptRequest(BaseModel):
    niche: str = "stoic_philosophy"
    topic: Optional[str] = None
    language: str = "pt-BR"


class PreviewAudioRequest(BaseModel):
    text: str
    voice: str = "pt-BR-AntonioNeural"
    rate: str = "+5%"


class ProduceVideoRequest(BaseModel):
    niche: str = "stoic_philosophy"
    topic: Optional[str] = None
    hook: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    b_roll_keywords: Optional[List[str]] = None
    voice: str = "pt-BR-AntonioNeural"
    voice_rate: str = "+5%"
    aspect_ratio: str = "9:16"
    highlight_color: str = "#FFE600"
    bgm_track: Optional[str] = "dark_stoic"
    bgm_volume: float = 0.15
    progress_bar: bool = True


class BatchProduceRequest(BaseModel):
    count: int = 3
    niche: str = "stoic_philosophy"
    voice: str = "pt-BR-AntonioNeural"
    aspect_ratio: str = "9:16"
    bgm_track: Optional[str] = "dark_stoic"
    highlight_color: str = "#FFE600"


def get_studio() -> SocialMediaVideoStudio:
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


@app.get("/api/meta")
def get_meta():
    """Retorna nichos, vozes, músicas e formatos disponíveis."""
    music_files = []
    if os.path.exists("assets/music"):
        for f in os.listdir("assets/music"):
            if f.endswith((".wav", ".mp3")):
                name = os.path.splitext(f)[0]
                if name not in music_files:
                    music_files.append(name)

    return {
        "niches": [{"id": k, "name": v["name"], "default_topic": v["default_topic"]} for k, v in NICHE_PROMPTS.items()],
        "voices": [{"id": k, "name": v} for k, v in AVAILABLE_VOICES.items()],
        "bgm_tracks": music_files,
        "aspect_ratios": [
            {"id": "9:16", "name": "9:16 (TikTok, Reels, Shorts)", "width": 1080, "height": 1920},
            {"id": "16:9", "name": "16:9 (YouTube Widescreen)", "width": 1920, "height": 1080},
            {"id": "1:1", "name": "1:1 (Feed Instagram, LinkedIn)", "width": 1080, "height": 1080},
        ],
        "colors": [
            {"name": "Amarelo Neon", "hex": "#FFE600"},
            {"name": "Verde Neon", "hex": "#00FF66"},
            {"name": "Ciano Elétrico", "hex": "#00F0FF"},
            {"name": "Rosa Magenta", "hex": "#FF0055"},
            {"name": "Branco Puro", "hex": "#FFFFFF"},
        ],
    }


@app.post("/api/generate-script")
def generate_script(req: GenerateScriptRequest):
    gemini_key = os.getenv("GEMINI_API_KEY")
    generator = GeminiScriptGenerator(api_key=gemini_key)
    result = generator.generate(niche=req.niche, topic=req.topic, language=req.language)
    return {
        "niche": result.niche,
        "topic": result.topic,
        "hook": result.hook,
        "body": result.body,
        "cta": result.cta,
        "full_text": result.full_text,
        "title": result.title,
        "description": result.description,
        "hashtags": result.hashtags,
        "b_roll_keywords": result.b_roll_keywords,
    }


@app.post("/api/preview-audio")
def preview_audio(req: PreviewAudioRequest):
    audio_gen = EdgeTTSAudioGenerator()
    preview_file = f"output/preview_{uuid.uuid4().hex[:8]}.mp3"
    subs_file = f"output/preview_{uuid.uuid4().hex[:8]}.srt"

    result = audio_gen.generate(
        text=req.text,
        voice=req.voice,
        rate=req.rate,
        output_audio=preview_file,
        output_subs=subs_file,
    )
    return {
        "audio_url": f"/{preview_file}",
        "duration": round(result.duration, 2),
    }


@app.post("/api/produce-video")
async def produce_video(req: ProduceVideoRequest):
    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {
        "id": job_id,
        "status": "processing",
        "progress": 5,
        "stage": "Iniciando produção...",
        "result": None,
    }

    asyncio.create_task(_run_produce_task(job_id, req))
    return {"job_id": job_id}


async def _run_produce_task(job_id: str, req: ProduceVideoRequest):
    def update_progress(stage: str, percent: int):
        if job_id in JOBS:
            JOBS[job_id]["stage"] = stage
            JOBS[job_id]["progress"] = percent

    try:
        studio = get_studio()

        ratio_map = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
        w, h = ratio_map.get(req.aspect_ratio, (1080, 1920))

        config = VideoConfig(
            aspect_ratio=req.aspect_ratio,
            width=w,
            height=h,
            highlight_color=req.highlight_color,
            bgm_track=req.bgm_track,
            bgm_volume=req.bgm_volume,
            progress_bar=req.progress_bar,
        )

        # Se o usuário enviou textos customizados do editor
        if req.hook and req.body:
            full = f"{req.hook} {req.body} {req.cta or ''}".strip()
            custom_script = ScriptResult(
                niche=req.niche,
                topic=req.topic or "personalizado",
                hook=req.hook,
                body=req.body,
                cta=req.cta or "",
                full_text=full,
                title=req.title or "Vídeo Viral",
                description=req.description or full,
                hashtags=req.hashtags or ["#shorts", "#reels"],
                b_roll_keywords=req.b_roll_keywords or ["dark aesthetic cinema", "motion dynamic"],
            )
            # Sobrescrever gerador de script para este job
            studio.script_gen.generate = lambda **kwargs: custom_script

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: studio.produce_single_video(
                niche=req.niche,
                topic=req.topic,
                voice=req.voice,
                voice_rate=req.voice_rate,
                config=config,
                progress_callback=update_progress,
            ),
        )

        rel_video = "/" + result.video_path
        rel_meta = "/" + result.metadata_path

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["stage"] = "Vídeo finalizado!"
        JOBS[job_id]["result"] = {
            "video_url": rel_video,
            "metadata_url": rel_meta,
            "title": result.script.title,
            "description": result.script.description,
            "hashtags": result.script.hashtags,
            "duration": round(result.duration, 1),
            "full_text": result.script.full_text,
        }
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["stage"] = f"Erro: {str(e)}"


@app.post("/api/produce-batch")
async def produce_batch(req: BatchProduceRequest):
    batch_job_id = "batch_" + uuid.uuid4().hex[:8]
    JOBS[batch_job_id] = {
        "id": batch_job_id,
        "status": "processing",
        "progress": 5,
        "stage": f"Iniciando esteira em lote de {req.count} vídeos...",
        "items": [],
        "completed_count": 0,
        "total_count": req.count,
    }

    asyncio.create_task(_run_batch_task(batch_job_id, req))
    return {"job_id": batch_job_id}


async def _run_batch_task(job_id: str, req: BatchProduceRequest):
    try:
        studio = get_studio()
        ratio_map = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
        w, h = ratio_map.get(req.aspect_ratio, (1080, 1920))

        config = VideoConfig(
            aspect_ratio=req.aspect_ratio,
            width=w,
            height=h,
            highlight_color=req.highlight_color,
            bgm_track=req.bgm_track,
        )

        def batch_progress(current: int, total: int, msg: str):
            if job_id in JOBS:
                percent = int((current - 1) / total * 100) + 10
                JOBS[job_id]["progress"] = percent
                JOBS[job_id]["stage"] = msg
                JOBS[job_id]["completed_count"] = current - 1

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: studio.produce_batch(
                count=req.count,
                niche=req.niche,
                voice=req.voice,
                config=config,
                progress_callback=batch_progress,
            ),
        )

        items = []
        for r in results:
            items.append(
                {
                    "video_url": "/" + r.video_path,
                    "title": r.script.title,
                    "duration": round(r.duration, 1),
                    "description": r.script.description,
                    "hashtags": r.script.hashtags,
                }
            )

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["stage"] = f"Lote de {req.count} vídeos concluído!"
        JOBS[job_id]["items"] = items
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["stage"] = f"Erro no lote: {str(e)}"


@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return JOBS[job_id]


@app.get("/", response_class=HTMLResponse)
def index_page():
    html_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>AllSocialMidia Web Studio</h1>"


def start_web_studio(port: int = 8000):
    print(f"\n🌐 Iniciando AllSocialMidia Web Studio em http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
