from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.memory import (
    MEMORY_ANALYSIS_SYSTEM_PROMPT,
    MEMORY_ANALYSIS_USER_PROMPT_TEMPLATE,
)
from packages.types.models import MemoryAnalysisInput, MemoryAnalysisOutput


class MemoryAgent(BaseAgent[MemoryAnalysisInput, MemoryAnalysisOutput]):
    async def run(self, inputs: MemoryAnalysisInput) -> MemoryAnalysisOutput:
        timeline_str = "\n".join(
            f"  - {e.timestamp}: {e.event_type}" +
            (f" — {str(e.event_data)[:100]}" if e.event_data else "")
            for e in inputs.timeline
        )
        activity_context = ""
        if inputs.recent_activity:
            activity_context = f"Recent activity:\n{inputs.recent_activity}"

        user_prompt = MEMORY_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            person_name=inputs.person_name,
            timeline_str=timeline_str or "No prior interaction",
            activity_context=activity_context,
        )

        return await self._llm_call(
            system_prompt=MEMORY_ANALYSIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=MemoryAnalysisOutput,
        )


async def analyze_memory(
    person_name: str,
    timeline: list,
    recent_activity: str | None = None,
    api_key: str | None = None,
) -> MemoryAnalysisOutput:
    from packages.types.models import TimelineEntry

    client = get_openai_client(api_key)
    agent = MemoryAgent(AgentContext(openai_client=client))
    return await agent.run(MemoryAnalysisInput(
        person_name=person_name,
        timeline=timeline,
        recent_activity=recent_activity,
    ))
