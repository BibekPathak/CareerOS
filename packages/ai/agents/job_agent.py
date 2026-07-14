from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.job import (
    JOB_ANALYSIS_SYSTEM_PROMPT,
    JOB_ANALYSIS_USER_PROMPT_TEMPLATE,
)
from packages.types.models import JobAnalysisInput, JobAnalysisOutput


class JobAnalysisAgent(BaseAgent[JobAnalysisInput, JobAnalysisOutput]):
    async def run(self, inputs: JobAnalysisInput) -> JobAnalysisOutput:
        experience_str = "\n".join(
            f"  - {e.role} at {e.company} ({e.duration}): {e.description[:200]}"
            for e in inputs.resume.experience
        )
        projects_str = "\n".join(
            f"  - {p.name}: {p.description[:200]} [{', '.join(p.technologies)}]"
            for p in inputs.resume.projects
        )
        context = f"\nAdditional context:\n{inputs.context}" if inputs.context else ""

        user_prompt = JOB_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            company_name=inputs.company_name,
            job_title=inputs.job_title,
            job_description=inputs.job_description,
            skills=", ".join(inputs.resume.skills),
            technologies=", ".join(inputs.resume.technologies),
            experience_str=experience_str,
            projects_str=projects_str,
            context=context,
        )

        return await self._llm_call(
            system_prompt=JOB_ANALYSIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=JobAnalysisOutput,
        )


async def analyze_job(
    job_title: str,
    job_description: str,
    company_name: str,
    resume: "ResumeOutput",
    context: str | None = None,
    api_key: str | None = None,
) -> JobAnalysisOutput:
    from packages.types.models import ResumeOutput

    client = get_openai_client(api_key)
    agent = JobAnalysisAgent(AgentContext(openai_client=client))
    return await agent.run(JobAnalysisInput(
        job_title=job_title,
        job_description=job_description,
        company_name=company_name,
        resume=resume,
        context=context,
    ))
