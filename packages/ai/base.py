from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)


class AgentContext(BaseModel):
    openai_client: AsyncOpenAI
    model: str = "gpt-4o"
    temperature: float = 0.3
    max_tokens: int = 4096


class BaseAgent(ABC, Generic[I, O]):
    def __init__(self, context: AgentContext):
        self.ctx = context

    @abstractmethod
    async def run(self, inputs: I) -> O:
        ...

    async def _llm_call(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[O],
    ) -> O:
        completion = await self.ctx.openai_client.beta.chat.completions.parse(
            model=self.ctx.model,
            temperature=self.ctx.temperature,
            max_tokens=self.ctx.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_model,
        )
        return completion.choices[0].message.parsed
