import json

from openai import OpenAI

from app.core.config import settings


class LLMService:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_json(self, prompt: str) -> dict:
        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )

        text = response.output_text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "overall_assessment": text,
                "main_risks": [],
                "missing_information": [],
                "suggested_test_cases": [],
                "recommended_next_actions": [],
            }
