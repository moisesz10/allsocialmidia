import re
from google import genai
from google.genai import types

from src.interfaces import IScriptGenerator


class GeminiScriptGenerator(IScriptGenerator):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self) -> str:
        prompt = (
            "Crie uma citação curta, poderosa e impactante de filosofia estóica ou motivação "
            "para um vídeo curto de TikTok/Reels. O texto deve ter entre 20 e 40 palavras no total, "
            "com uma introdução intrigante e uma conclusão forte. Responda APENAS com a citação, "
            "sem aspas ou explicações adicionais."
        )

        print("Gerando roteiro com a API do Gemini...")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            ),
        )

        text = response.text.strip()
        text = re.sub(r'^["\']|["\']$', "", text).strip()
        return text
