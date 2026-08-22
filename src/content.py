import json
import logging
from typing import Any, Dict, Optional

from google import genai
from google.genai import types

from src.interfaces import IScriptGenerator
from src.models import ScriptResult, YouTubeContentPackage

logger = logging.getLogger(__name__)

NICHE_PROMPTS: Dict[str, Any] = {
    "stoic_philosophy": {
        "name": "Filosofia Estóica & Sabedoria",
        "system": (
            "Você é um criador de conteúdo especialista no YouTube (Shorts e Vídeos Longos) sobre Filosofia Estóica, Marco Aurélio e reflexões profundas. "
        ),
        "default_topic": "o poder do silêncio e o controle das emoções",
        "b_roll_fallback": ["ancient statue", "dark storm clouds", "lone mountain fog", "ocean waves crashing"],
    },
    "curiosities": {
        "name": "Curiosidades & Fatos Inacreditáveis",
        "system": (
            "Você é um criador de vídeos de curiosidades para o YouTube. "
            "Comece com uma pergunta que quebre o padrão cognitivo do espectador."
        ),
        "default_topic": "um fato bizarro sobre o oceano profundo que quase ninguém conhece",
        "b_roll_fallback": ["deep ocean bioluminescence", "mysterious underwater abyss", "galaxy stars space"],
    },
    "stories_mystery": {
        "name": "Micro-Histórias & Mistério",
        "system": (
            "Você é um narrador de histórias de mistério e suspense no YouTube com reviravoltas finais. "
            "Prenda a atenção desde a primeira sílaba com atmosfera sombria."
        ),
        "default_topic": "um enigma não resolvido do século passado",
        "b_roll_fallback": ["dark foggy forest", "old vintage room shadow", "abandoned hallway night"],
    },
    "motivation": {
        "name": "Motivação & Disciplina Brutal",
        "system": (
            "Você é um mentor de alta performance no YouTube. "
            "Use uma linguagem direta, sem filtros, focada em foco e superação."
        ),
        "default_topic": "porque a consistência silenciosa vence o talento barulhento",
        "b_roll_fallback": ["intense workout gym dark", "running at sunrise road", "city skyscraper top view"],
    },
    "tech_future": {
        "name": "Tecnologia & Futuro",
        "system": (
            "Você é um especialista em inovação tecnológica, IA e tendências futuras no YouTube. "
            "Explique de forma visual e instigante como o mundo está mudando."
        ),
        "default_topic": "como a inteligência artificial vai transformar o trabalho em 2 anos",
        "b_roll_fallback": ["futuristic server room glowing", "cyberpunk city neon", "digital network particles"],
    },
    "finance_wealth": {
        "name": "Finanças & Mentalidade de Riqueza",
        "system": (
            "Você é um estrategista de finanças e investimentos no YouTube. "
            "Ensine uma lição prática sobre dinheiro e liberdade financeira."
        ),
        "default_topic": "a regra dos 3 passos que os ricos seguem para nunca perder dinheiro",
        "b_roll_fallback": ["luxury penthouse night view", "gold vault counting money", "modern architecture minimal"],
    },
}

FALLBACK_PACKAGES: Dict[str, YouTubeContentPackage] = {
    "stoic_philosophy": YouTubeContentPackage(
        short_script=ScriptResult(
            niche="stoic_philosophy",
            topic="controle emocional",
            hook="Você não pode controlar o que acontece ao seu redor.",
            body="Mas tem poder absoluto sobre como reage. A sua paz interior é o seu maior superpoder.",
            cta="Assista ao vídeo completo no canal para entender.",
            full_text="Você não pode controlar o que acontece ao seu redor. Mas tem poder absoluto sobre como reage. A sua paz interior é o seu maior superpoder. Assista ao vídeo completo no canal para entender.",
            title="O Poder do Autocontrole Estoico",
            description="A sua mente é a sua única fortaleza inabalável. Assista ao vídeo completo! #estoicismo #filosofia #sabedoria #youtube",
            video_type="short",
            hashtags=["#estoicismo", "#filosofia", "#sabedoria", "#youtube"],
            b_roll_keywords=["ancient roman statue", "dramatic storm clouds"],
        ),
        long_script=ScriptResult(
            niche="stoic_philosophy",
            topic="controle emocional",
            hook="Hoje vamos explorar o verdadeiro significado do poder sobre si mesmo.",
            body="A filosofia estoica nos ensina que não somos perturbados pelas coisas, mas pela visão que temos delas. Epicteto, um ex-escravo que se tornou um dos maiores filósofos de Roma, disse que apenas os tolos se enfurecem com as circunstâncias externas. O vídeo de hoje mergulha na prática da dicotomia do controle...",
            cta="Se inscreva no canal para mais reflexões profundas.",
            full_text="Hoje vamos explorar o verdadeiro significado do poder sobre si mesmo. A filosofia estoica nos ensina que não somos perturbados pelas coisas, mas pela visão que temos delas. Epicteto, um ex-escravo que se tornou um dos maiores filósofos de Roma, disse que apenas os tolos se enfurecem com as circunstâncias externas. O vídeo de hoje mergulha na prática da dicotomia do controle. Se inscreva no canal para mais reflexões profundas.",
            title="Como ter Controle Emocional - Filosofia Estoica",
            description="Descubra o segredo do controle emocional com a filosofia estoica. Inscreva-se! #estoicismo #foco",
            video_type="long",
            hashtags=["#estoicismo", "#filosofia", "#desenvolvimentopessoal"],
            b_roll_keywords=["ancient roman statue", "ocean waves dark", "lone figure walking"],
        ),
    ),
}


class GeminiScriptGenerator(IScriptGenerator):
    """Gerador de pacotes de conteúdo para YouTube (Shorts e Vídeos Longos) com Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key) if api_key and api_key != "sua_chave_api_aqui" else None

    def generate(
        self,
        niche: str = "stoic_philosophy",
        topic: Optional[str] = None,
        language: str = "pt-BR",
    ) -> YouTubeContentPackage:
        """Gera um pacote com roteiro de Short e roteiro de Vídeo Longo interligados."""
        niche_info = NICHE_PROMPTS.get(niche, NICHE_PROMPTS["stoic_philosophy"])
        chosen_topic = topic or niche_info["default_topic"]

        if not self.client:
            logger.warning("Gemini Client não inicializado. Usando pacote de backup.")
            return self._get_fallback_package(niche, chosen_topic)

        prompt = (
            f"Você é o diretor de criação de um canal de sucesso exclusivo no YouTube.\n"
            f"O objetivo é gerar um pacote de conteúdo contendo 1 YouTube Short (Teaser) e 1 Vídeo Longo para o canal.\n"
            f"Nicho: '{niche_info['name']}'.\n"
            f"Tema: '{chosen_topic}'.\n"
            f"Idioma: {language}.\n\n"
            f"DIRETRIZES:\n"
            f"- O Short deve ser curto, magnético e terminar com uma chamada forte convidando o público a assistir o vídeo longo no canal.\n"
            f"- O Vídeo Longo deve aprofundar o tema com introdução envolvente, desenvolvimento e conclusão.\n\n"
            f"ESTRUTURA OBRIGATÓRIA (responda estritamente em formato JSON válido):\n"
            f"{{\n"
            f'  "short": {{\n'
            f'    "hook": "Frase magnética do short (até 10 palavras)",\n'
            f'    "body": "Corpo do short com 30 a 50 palavras",\n'
            f'    "cta": "Chamada convidando pro vídeo longo no canal (máx 10 palavras)",\n'
            f'    "title": "Título viral do short",\n'
            f'    "description": "Legenda curta do short",\n'
            f'    "hashtags": ["#tag1", "#shorts"],\n'
            f'    "b_roll_keywords": ["keyword 1", "keyword 2"]\n'
            f'  }},\n'
            f'  "long": {{\n'
            f'    "hook": "Introdução forte do vídeo longo (até 20 palavras)",\n'
            f'    "body": "Desenvolvimento aprofundado do tema com 150 a 250 palavras",\n'
            f'    "cta": "Chamada para inscrição e like no canal",\n'
            f'    "title": "Título pesquisável do vídeo longo",\n'
            f'    "description": "Legenda/descrição completa para o vídeo longo do YouTube",\n'
            f'    "hashtags": ["#tag1", "#tag2"],\n'
            f'    "b_roll_keywords": ["keyword 1", "keyword 2"]\n'
            f'  }}\n'
            f"}}\n"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.75,
                ),
            )
            text_response = response.text
            if not text_response:
                raise ValueError("Resposta da IA vazia.")
            data = json.loads(text_response)

            # Short Script
            short_data = data.get("short", {})
            s_hook = short_data.get("hook", "").strip()
            s_body = short_data.get("body", "").strip()
            s_cta = short_data.get("cta", "").strip()
            s_full_text = f"{s_hook} {s_body} {s_cta}".strip()
            short_script = ScriptResult(
                niche=niche,
                topic=chosen_topic,
                hook=s_hook,
                body=s_body,
                cta=s_cta,
                full_text=s_full_text,
                title=short_data.get("title", f"Teaser: {niche_info['name']}"),
                description=short_data.get("description", s_full_text),
                video_type="short",
                hashtags=short_data.get("hashtags", ["#shorts", "#youtube"]),
                b_roll_keywords=short_data.get("b_roll_keywords", niche_info["b_roll_fallback"]),
            )

            # Long Script
            long_data = data.get("long", {})
            l_hook = long_data.get("hook", "").strip()
            l_body = long_data.get("body", "").strip()
            l_cta = long_data.get("cta", "").strip()
            l_full_text = f"{l_hook} {l_body} {l_cta}".strip()
            long_script = ScriptResult(
                niche=niche,
                topic=chosen_topic,
                hook=l_hook,
                body=l_body,
                cta=l_cta,
                full_text=l_full_text,
                title=long_data.get("title", f"Vídeo Completo: {niche_info['name']}"),
                description=long_data.get("description", l_full_text),
                video_type="long",
                hashtags=long_data.get("hashtags", ["#youtube"]),
                b_roll_keywords=long_data.get("b_roll_keywords", niche_info["b_roll_fallback"]),
            )

            return YouTubeContentPackage(short_script=short_script, long_script=long_script)

        except Exception as err:
            logger.error(f"Erro ao gerar com Gemini: {err}. Usando pacote de backup.")
            return self._get_fallback_package(niche, chosen_topic)

    def _get_fallback_package(self, niche: str, topic: str) -> YouTubeContentPackage:
        if niche in FALLBACK_PACKAGES:
            return FALLBACK_PACKAGES[niche]

        # Backup Genérico
        short_script = ScriptResult(
            niche=niche,
            topic=topic,
            hook="Um segredo mudará sua vida.",
            body="Aprenda a focar naquilo que importa. O resto é distração.",
            cta="Veja o vídeo completo no canal.",
            full_text="Um segredo mudará sua vida. Aprenda a focar naquilo que importa. O resto é distração. Veja o vídeo completo no canal.",
            title="Segredo Revelado",
            description="Assista ao vídeo completo! #shorts",
            video_type="short",
        )
        long_script = ScriptResult(
            niche=niche,
            topic=topic,
            hook="Hoje vamos aprofundar um segredo de sucesso.",
            body="A chave para grandes realizações está na sua rotina. Pessoas bem sucedidas...",
            cta="Inscreva-se no canal para mais conteúdos.",
            full_text="Hoje vamos aprofundar um segredo de sucesso. A chave para grandes realizações está na sua rotina. Pessoas bem sucedidas... Inscreva-se no canal para mais conteúdos.",
            title="Como alcançar o sucesso - Completo",
            description="Tudo o que você precisa saber sobre o sucesso. Inscreva-se! #sucesso #foco",
            video_type="long",
        )
        return YouTubeContentPackage(short_script=short_script, long_script=long_script)
