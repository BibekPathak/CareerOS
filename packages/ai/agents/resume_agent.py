from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.resume import RESUME_SYSTEM_PROMPT
from packages.types.models import ResumeInput, ResumeOutput


class ResumeAgent(BaseAgent[ResumeInput, ResumeOutput]):
    async def run(self, inputs: ResumeInput) -> ResumeOutput:
        return await self._llm_call(
            system_prompt=RESUME_SYSTEM_PROMPT,
            user_prompt=f"Parse the following resume text and return structured data:\n\n{inputs.raw_text}",
            response_model=ResumeOutput,
        )


async def parse_resume(raw_text: str, api_key: str | None = None) -> ResumeOutput:
    client = get_openai_client(api_key)
    agent = ResumeAgent(AgentContext(openai_client=client))
    return await agent.run(ResumeInput(raw_text=raw_text))
