from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.outreach import OUTREACH_SYSTEM_PROMPT
from packages.types.models import OutreachInput, OutreachOutput


class OutreachAgent(BaseAgent[OutreachInput, OutreachOutput]):
    async def run(self, inputs: OutreachInput) -> OutreachOutput:
        user_prompt = (
            f"--- User Resume ---\n"
            f"Skills: {', '.join(inputs.resume.skills)}\n"
            f"Technologies: {', '.join(inputs.resume.technologies)}\n"
            f"Experience:\n" + "\n".join(
                f"  - {e.role} at {e.company} ({e.duration}): {e.description[:150]}"
                for e in inputs.resume.experience
            ) + "\n"
            f"Projects:\n" + "\n".join(
                f"  - {p.name}: {p.description[:150]} [{', '.join(p.technologies)}]"
                for p in inputs.resume.projects
            ) + "\n\n"
            f"--- Target Person ---\n"
            f"Name: {inputs.target_person.name}\n"
            f"Score: {inputs.target_person.score}\n"
            f"Explanation: {inputs.target_person.explanation}\n"
            f"Summary: {inputs.person_summary}\n\n"
            f"--- Company ---\n{inputs.company_name}\n"
            f"Target role: {inputs.target_role or 'Not specified'}\n\n"
            f"Generate 5 personalized outreach messages referencing real overlap between the user and {inputs.target_person.name}."
        )
        return await self._llm_call(
            system_prompt=OUTREACH_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=OutreachOutput,
        )


async def generate_outreach(
    resume: "ResumeOutput",
    target_person: "RankedPerson",
    person_summary: str,
    company_name: str,
    target_role: str | None = None,
    api_key: str | None = None,
) -> OutreachOutput:
    from packages.types.models import ResumeOutput, RankedPerson
    client = get_openai_client(api_key)
    agent = OutreachAgent(AgentContext(openai_client=client))
    return await agent.run(OutreachInput(
        resume=resume,
        target_person=target_person,
        person_summary=person_summary,
        company_name=company_name,
        target_role=target_role,
    ))
