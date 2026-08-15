import json
import logging
from typing import Dict, Optional

from google import genai
from google.genai import types

from src.interfaces import IScriptGenerator
from src.models import ScriptResult

logger = logging.getLogger(__name__)

NICHE_PROMPTS: Dict[str, Dict[str, str]] = {
    "stoic_philosophy": {
        "name": "Filosofia Estóica & Sabedoria",
        "system": (
            "Você é um criador de conteúdo viral especialista em Filosofia Estóica, Marco Aurélio e reflexões profundas. "
            "Crie um roteiro magnético e curto para TikTok/Reels/Shorts."
        ),
        "default_topic": "o poder do silêncio e o controle das emoções",
        "b_roll_fallback": ["ancient statue", "dark storm clouds", "lone mountain fog", "ocean waves crashing"],
    },
    "curiosities": {
        "name": "Curiosidades & Fatos Inacreditáveis",
        "system": (
            "Você é um criador de vídeos de curiosidades rápidas que viralizam em segundos. "
            "Comece com uma pergunta que quebre o padrão cognitivo do espectador."
        ),
        "default_topic": "um fato bizarro sobre o oceano profundo que quase ninguém conhece",
        "b_roll_fallback": ["deep ocean bioluminescence", "mysterious underwater abyss", "galaxy stars space"],
    },
    "stories_mystery": {
        "name": "Micro-Histórias & Mistério",
        "system": (
            "Você é um narrador de micro-histórias de mistério e suspense com reviravolta final. "
            "Prenda a atenção desde a primeira sílaba com atmosfera sombria."
        ),
        "default_topic": "um enigma não resolvido do século passado",
        "b_roll_fallback": ["dark foggy forest", "old vintage room shadow", "abandoned hallway night"],
    },
    "motivation": {
        "name": "Motivação & Disciplina Brutal",
        "system": (
            "Você é um mentor de alta performance e autodisciplina. "
            "Use uma linguagem direta, sem filtros, focada em foco e superação."
        ),
        "default_topic": "porque a consistência silenciosa vence o talento barulhento",
        "b_roll_fallback": ["intense workout gym dark", "running at sunrise road", "city skyscraper top view"],
    },
    "tech_future": {
        "name": "Tecnologia & Futuro",
        "system": (
            "Você é um especialista em inovação tecnológica, IA e tendências futuras. "
            "Explique de forma visual e instigante como o mundo está mudando."
        ),
        "default_topic": "como a inteligência artificial vai transformar o trabalho em 2 anos",
        "b_roll_fallback": ["futuristic server room glowing", "cyberpunk city neon", "digital network particles"],
    },
    "finance_wealth": {
        "name": "Finanças & Mentalidade de Riqueza",
        "system": (
            "Você é um estrategista de finanças e investimentos para jovens ambiciosos. "
            "Ensine uma lição prática sobre dinheiro e liberdade financeira."
        ),
        "default_topic": "a regra dos 3 passos que os ricos seguem para nunca perder dinheiro",
        "b_roll_fallback": ["luxury penthouse night view", "gold vault counting money", "modern architecture minimal"],
    },
}

FALLBACK_SCRIPTS: Dict[str, ScriptResult] = {
    "stoic_philosophy": ScriptResult(
        niche="stoic_philosophy",
        topic="controle emocional",
        hook="Você não pode controlar o que acontece ao seu redor.",
        body="Mas tem poder absoluto sobre como reage a cada acontecimento. A sua paz interior é o seu maior superpoder. Não a entregue a ninguém de graça.",
        cta="Siga para fortalecer sua mente todos os dias.",
        full_text="Você não pode controlar o que acontece ao seu redor. Mas tem poder absoluto sobre como reage a cada acontecimento. A sua paz interior é o seu maior superpoder. Não a entregue a ninguém de graça. Siga para fortalecer sua mente todos os dias.",
        title="O Poder do Autocontrole Estoico",
        description="A sua mente é a sua única fortaleza inabalável. 🏛️\n\n#estoicismo #filosofia #sabedoria #desenvolvimentopessoal #mindset",
        hashtags=["#estoicismo", "#filosofia", "#sabedoria", "#mentalidade", "#foco"],
        b_roll_keywords=["ancient roman statue", "dramatic storm clouds", "ocean waves dark"],
    ),
    "curiosities": ScriptResult(
        niche="curiosities",
        topic="profundezas do oceano",
        hook="Você sabia que nós conhecemos mais sobre o espaço do que sobre nossos próprios oceanos?",
        body="Mais de 80 por cento do fundo do mar permanece inexplorado e na escuridão total. Existem criaturas gigantescas que nunca viram a luz do sol.",
        cta="Comente o que você acha que existe lá embaixo!",
        full_text="Você sabia que nós conhecemos mais sobre o espaço do que sobre nossos próprios oceanos? Mais de 80 por cento do fundo do mar permanece inexplorado e na escuridão total. Existem criaturas gigantescas que nunca viram a luz do sol. Comente o que você acha que existe lá embaixo!",
        title="O Segredo Macabro dos Oceanos",
        description="O que realmente se esconde no abismo marinho? 🌊👁️\n\n#curiosidades #fatosdesconhecidos #ciencia #oceano #misterio",
        hashtags=["#curiosidades", "#fatoscuriosos", "#oceano", "#misterios", "#planeta"],
        b_roll_keywords=["deep dark ocean", "underwater abyss glow", "mysterious sea creatures"],
    ),
    "motivation": ScriptResult(
        niche="motivation",
        topic="disciplina diária",
        hook="O mundo não se importa com a sua motivação temporária.",
        body="O que define seu sucesso é o que você faz nos dias em que não tem vontade de levantar. A disciplina vence qualquer desculpa.",
        cta="Salve este vídeo para quando precisar lembrar quem você é.",
        full_text="O mundo não se importa com a sua motivação temporária. O que define seu sucesso é o que você faz nos dias em que não tem vontade de levantar. A disciplina vence qualquer desculpa. Salve este vídeo para quando precisar lembrar quem você é.",
        title="A Disciplina Silenciosa",
        description="Faça o que precisa ser feito, especialmente quando for difícil. 🔥\n\n#motivacao #disciplina #foco #sucesso #treino",
        hashtags=["#motivacao", "#disciplina", "#foco", "#mindsetdesucesso", "#superacao"],
        b_roll_keywords=["intense gym workout", "running sunrise dark", "dramatic city night"],
    ),
}


class GeminiScriptGenerator(IScriptGenerator):
    """Gerador de roteiros inteligentes multi-nicho com Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key) if api_key and api_key != "sua_chave_api_aqui" else None

    def generate(
        self,
        niche: str = "stoic_philosophy",
        topic: Optional[str] = None,
        language: str = "pt-BR",
    ) -> ScriptResult:
        """Gera um roteiro estruturado com gancho, corpo, chamada para ação e metadados."""
        niche_info = NICHE_PROMPTS.get(niche, NICHE_PROMPTS["stoic_philosophy"])
        chosen_topic = topic or niche_info["default_topic"]

        if not self.client:
            logger.warning("Gemini Client não inicializado. Usando roteiro de backup de alta qualidade.")
            return self._get_fallback_script(niche, chosen_topic)

        prompt = (
            f"Você é o diretor de criação de uma produtora de vídeos curtos (Reels, TikTok, Shorts).\n"
            f"Gere um roteiro impactante no nicho: '{niche_info['name']}'.\n"
            f"Tema: '{chosen_topic}'.\n"
            f"Idioma: {language}.\n\n"
            f"ESTRUTURA OBRIGATÓRIA (responda estritamente em formato JSON válido):\n"
            f"{{\n"
            f'  "hook": "Uma frase inicial magnética e intrigante de até 10 palavras que pare o scroll",\n'
            f'  "body": "Corpo da mensagem direto, fluido e poderoso com 30 a 50 palavras",\n'
            f'  "cta": "Chamada para ação curta incentivando curtir, comentar ou seguir (máx 10 palavras)",\n'
            f'  "title": "Título viral de 3 a 7 palavras",\n'
            f'  "description": "Legenda completa do post com 2 parágrafos curtos para Instagram/TikTok",\n'
            f'  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],\n'
            f'  "b_roll_keywords": ["keyword 1 in english", "keyword 2 in english", "keyword 3 in english"]\n'
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
            data = json.loads(response.text)
            hook = data.get("hook", "").strip()
            body = data.get("body", "").strip()
            cta = data.get("cta", "").strip()
            full_text = f"{hook} {body} {cta}".strip()

            return ScriptResult(
                niche=niche,
                topic=chosen_topic,
                hook=hook,
                body=body,
                cta=cta,
                full_text=full_text,
                title=data.get("title", f"Vídeo de {niche_info['name']}"),
                description=data.get("description", full_text),
                hashtags=data.get("hashtags", ["#shorts", "#viral", "#reels"]),
                b_roll_keywords=data.get("b_roll_keywords", niche_info["b_roll_fallback"]),
            )
        except Exception as err:
            logger.error(f"Erro ao gerar com Gemini: {err}. Usando roteiro de backup.")
            return self._get_fallback_script(niche, chosen_topic)

    def _get_fallback_script(self, niche: str, topic: str) -> ScriptResult:
        if niche in FALLBACK_SCRIPTS:
            base = FALLBACK_SCRIPTS[niche]
            return base

        return ScriptResult(
            niche=niche,
            topic=topic,
            hook="Existe um segredo que poucas pessoas estão dispostas a admitir.",
            body="Quando você decide parar de dar desculpas e foca cem por cento naquilo que pode controlar, seus resultados mudam radicalmente.",
            cta="Siga o perfil para mais conteúdos como esse.",
            full_text="Existe um segredo que poucas pessoas estão dispostas a admitir. Quando você decide parar de dar desculpas e foca cem por cento naquilo que pode controlar, seus resultados mudam radicalmente. Siga o perfil para mais conteúdos como esse.",
            title="A Verdade Sobre o Sucesso",
            description="Foco total naquilo que você controla. 🔥\n\n#foco #disciplina #mentalidade #evoluir #shorts",
            hashtags=["#foco", "#disciplina", "#mentalidade", "#shorts", "#reels"],
            b_roll_keywords=["dark aesthetic minimal", "lone figure walking dark", "stormy sky timelapsed"],
        )
