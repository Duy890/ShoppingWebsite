import json
import openai
from app.core.config import settings

class OpenAIFormatter:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)

    def format_response(self, intent: str, entities: dict, data: dict, original_message: str) -> str:
        if not self.client:
            return original_message

        try:
            # System prompt with strict guardrails
            system_prompt = (
                "You are a helpful chatbot for an electronics store. "
                "Your task is to format a conversational response based on the structured data provided by the backend engines. "
                "CRITICAL RULES:\n"
                "1. DO NOT invent any facts, technical specifications, or products. Only use what is provided.\n"
                "2. DO NOT create fake benchmarks or performance claims. Use ONLY the data provided in 'Backend Data'.\n"
                "3. If the data is empty or indicates no results, explain this clearly to the user without making up alternatives unless they are explicitly in the data.\n"
                "4. Your goal is to improve readability, summarize findings, and explain technical details naturally.\n"
                "5. Use Markdown for formatting (bolding, lists, tables) to make the information easy to scan.\n"
                "6. Maintain a professional, helpful, and concise tone.\n"
                "7. If the 'Original System Message' provides a good explanation, you can use it as a base and enhance it.\n"
                "8. Never mention that you are an AI or using an API. Just respond as the store's assistant."
            )

            # Prepare a clean version of the data for the prompt
            # We don't want to overwhelm the context with huge JSON if not needed, 
            # but for now we'll pass it and see.
            user_prompt = f"""
Intent: {intent}
Entities: {json.dumps(entities, ensure_ascii=False)}
Backend Data: {json.dumps(data, ensure_ascii=False)}
Original System Message: {original_message}

Please provide a polished, natural-sounding response to the user.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            # Log error and fallback to original message
            print(f"OpenAI Formatting Error: {e}")
            return original_message

openai_formatter = OpenAIFormatter()
