from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.outreach_intelligence import (
    OUTREACH_INTELLIGENCE_SYSTEM_PROMPT,
    OUTREACH_INTELLIGENCE_USER_PROMPT_TEMPLATE,
)
from packages.types.models import OutreachIntelligenceInput, OutreachIntelligenceOutput


class OutreachIntelligenceAgent(BaseAgent[OutreachIntelligenceInput, OutreachIntelligenceOutput]):
    async def run(self, inputs: OutreachIntelligenceInput) -> OutreachIntelligenceOutput:
        experience_str = "\n".join(
            f"  - {e.role} at {e.company} ({e.duration}): {e.description[:200]}"
            for e in inputs.resume.experience
        )
        projects_str = "\n".join(
            f"  - {p.name}: {p.description[:200]} [{', '.join(p.technologies)}]"
            for p in inputs.resume.projects
        )

        user_prompt = OUTREACH_INTELLIGENCE_USER_PROMPT_TEMPLATE.format(
            person_name=inputs.person_name,
            person_role=inputs.person_role,
            person_summary=inputs.person_summary,
            expertise_str=", ".join(inputs.expertise_areas),
            company_name=inputs.company_name,
            skills=", ".join(inputs.resume.skills),
            technologies=", ".join(inputs.resume.technologies),
            experience_str=experience_str,
            projects_str=projects_str,
        )

        return await self._llm_call(
            system_prompt=OUTREACH_INTELLIGENCE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=OutreachIntelligenceOutput,
        )


async def generate_outreach_intelligence(
    person_name: str,
    person_role: str | None,
    person_summary: str,
    expertise_areas: list[str],
    company_name: str,
    resume: "ResumeOutput",
    api_key: str | None = None,
) -> OutreachIntelligenceOutput:
    from packages.types.models import ResumeOutput

    client = get_openai_client(api_key)
    agent = OutreachIntelligenceAgent(AgentContext(openai_client=client))
    return await agent.run(OutreachIntelligenceInput(
        person_name=person_name,
        person_role=person_role,
        person_summary=person_summary,
        expertise_areas=expertise_areas,
        company_name=company_name,
        resume=resume,
    ))
