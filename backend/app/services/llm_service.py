from openai import OpenAI
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def ask_llm(prompt: str, max_tokens: int = 1000, max_retries: int = 3) -> str:
    """Call the LLM with automatic retry on rate-limit errors."""
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e).lower()

            if "rate" in error_str or "429" in error_str:
                wait_time = (attempt + 1) * 5
                print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                raise e

    raise last_error