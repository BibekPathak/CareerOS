from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.daily import (
    DAILY_BRIEF_SYSTEM_PROMPT,
    DAILY_BRIEF_USER_PROMPT_TEMPLATE,
)
from packages.types.models import DailyBriefInput, DailyBriefOutput


class DailyAgent(BaseAgent[DailyBriefInput, DailyBriefOutput]):
    async def run(self, inputs: DailyBriefInput) -> DailyBriefOutput:
        def fmt(items: list[dict]) -> str:
            if not items:
                return "None"
            return "\n".join(
                f"  - {i.get('title', '')}: {i.get('description', '')}"
                + (f" [{i.get('urgency', 'medium')}]" if i.get('urgency') else "")
                for i in items
            )

        user_prompt = DAILY_BRIEF_USER_PROMPT_TEMPLATE.format(
            new_jobs_str=fmt(inputs.new_jobs),
            recruiter_changes_str=fmt(inputs.recruiter_changes),
            engagement_str=fmt(inputs.engagement_signals),
            follow_ups_str=fmt(inputs.follow_ups_due),
            company_news_str=fmt(inputs.company_news),
        )

        return await self._llm_call(
            system_prompt=DAILY_BRIEF_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=DailyBriefOutput,
        )


async def generate_daily_brief(
    new_jobs: list[dict] | None = None,
    recruiter_changes: list[dict] | None = None,
    engagement_signals: list[dict] | None = None,
    follow_ups_due: list[dict] | None = None,
    company_news: list[dict] | None = None,
    api_key: str | None = None,
) -> DailyBriefOutput:
    client = get_openai_client(api_key)
    agent = DailyAgent(AgentContext(openai_client=client))
    return await agent.run(DailyBriefInput(
        new_jobs=new_jobs or [],
        recruiter_changes=recruiter_changes or [],
        engagement_signals=engagement_signals or [],
        follow_ups_due=follow_ups_due or [],
        company_news=company_news or [],
    ))
