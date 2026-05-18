from openai import AzureOpenAI
from utils.logger import log_event
import config

_client = None


def get_client() -> AzureOpenAI:
    global _client
    if _client is None:
        _client = AzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY,
            azure_endpoint=config.ENDPOINT,
            api_version=config.API_VERSION,
        )
    return _client


def call_llm(system: str, user: str, max_tokens: int = 2000, caller: str = "LLM") -> str:
    response = get_client().chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_completion_tokens=max_tokens,
    )

    usage = response.usage
    log_event(caller, "LLM call", {
        "model": config.MODEL,
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "total_tokens": usage.total_tokens if usage else 0,
    })

    return response.choices[0].message.content
