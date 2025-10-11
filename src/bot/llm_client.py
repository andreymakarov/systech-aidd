import logging

from openai import AsyncOpenAI

from bot.config import Config


class LLMClient:
    """Клиент для работы с LLM через OpenRouter API"""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.openrouter_api_key, base_url=config.openrouter_base_url
        )

    async def generate_response(self, messages: list[dict[str, str]]) -> str:
        """Генерация ответа от LLM с учетом истории диалога"""
        try:
            logging.info(f"Sending request to LLM (model: {self.config.openrouter_model})")

            response = await self.client.chat.completions.create(
                model=self.config.openrouter_model,
                messages=messages,  # type: ignore[arg-type]
            )

            answer = response.choices[0].message.content
            if answer is None:
                raise ValueError("LLM returned empty response")

            logging.info(f"LLM response received ({len(answer)} chars)")
            return answer

        except Exception as e:
            logging.error(f"Error calling LLM API: {type(e).__name__}: {e}")
            raise
