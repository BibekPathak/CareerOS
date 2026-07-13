from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.ranking import RANKING_SYSTEM_PROMPT
from packages.types.models import RankingInput, RankingOutput


class RankingAgent(BaseAgent[RankingInput, RankingOutput]):
    async def run(self, inputs: RankingInput) -> RankingOutput:
        people_str = "\n".join(
            f"- {p.name} ({p.role or 'Unknown role'}): {p.summary[:200]}"
            for p in inputs.people
        )
        user_prompt = (
            f"Company: {inputs.company_name}\n"
            f"Target role: {inputs.target_role or 'Not specified'}\n\n"
            f"--- User Resume ---\n"
            f"Skills: {', '.join(inputs.resume.skills)}\n"
            f"Technologies: {', '.join(inputs.resume.technologies)}\n"
            f"Experience: {', '.join(e.company + ' (' + e.role + ')' for e in inputs.resume.experience)}\n"
            f"Seniority: {inputs.resume.seniority}\n\n"
            f"--- People to Rank ---\n{people_str}\n\n"
            f"Rank each person by relevance for networking to get a job at {inputs.company_name}."
        )
        return await self._llm_call(
            system_prompt=RANKING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RankingOutput,
        )


async def rank_people(
    company_name: str,
    resume: "ResumeOutput",
    people: list["Person"],
    target_role: str | None = None,
    api_key: str | None = None,
) -> RankingOutput:
    from packages.types.models import ResumeOutput, Person
    client = get_openai_client(api_key)
    agent = RankingAgent(AgentContext(openai_client=client))
    return await agent.run(RankingInput(
        company_name=company_name,
        resume=resume,
        people=people,
        target_role=target_role,
    ))
