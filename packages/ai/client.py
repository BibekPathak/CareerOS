from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def get_openai_client(api_key: str | None = None) -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=api_key)
    return _client
