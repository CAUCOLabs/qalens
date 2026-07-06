from openai import OpenAI

from app.core.config import settings


class LLMService:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_text(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )

        return response.output_text
