from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.resume_matching import (
    RESUME_MATCHING_SYSTEM_PROMPT,
    RESUME_MATCHING_USER_PROMPT_TEMPLATE,
)
from packages.types.models import ResumeMatchInput, ResumeMatchOutput


class ResumeMatchingAgent(BaseAgent[ResumeMatchInput, ResumeMatchOutput]):
    async def run(self, inputs: ResumeMatchInput) -> ResumeMatchOutput:
        experience_str = "\n".join(
            f"  - {e.role} at {e.company} ({e.duration}): {e.description[:200]}"
            for e in inputs.resume.experience
        )
        projects_str = "\n".join(
            f"  - {p.name}: {p.description[:200]} [{', '.join(p.technologies)}]"
            for p in inputs.resume.projects
        )

        user_prompt = RESUME_MATCHING_USER_PROMPT_TEMPLATE.format(
            job_title=inputs.job_title,
            company_name=inputs.company_name,
            job_description=inputs.job_description,
            job_skills_str=", ".join(inputs.job_skills),
            skills=", ".join(inputs.resume.skills),
            technologies=", ".join(inputs.resume.technologies),
            experience_str=experience_str,
            projects_str=projects_str,
        )

        return await self._llm_call(
            system_prompt=RESUME_MATCHING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ResumeMatchOutput,
        )


async def match_resume_to_job(
    job_title: str,
    job_description: str,
    job_skills: list[str],
    company_name: str,
    resume: "ResumeOutput",
    api_key: str | None = None,
) -> ResumeMatchOutput:
    from packages.types.models import ResumeOutput

    client = get_openai_client(api_key)
    agent = ResumeMatchingAgent(AgentContext(openai_client=client))
    return await agent.run(ResumeMatchInput(
        job_title=job_title,
        job_description=job_description,
        job_skills=job_skills,
        company_name=company_name,
        resume=resume,
    ))
