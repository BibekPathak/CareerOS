from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.planner import (
    CAREER_PLANNER_SYSTEM_PROMPT,
    CAREER_PLANNER_USER_PROMPT_TEMPLATE,
)
from packages.types.models import CareerGoalInput, CareerPlanOutput


class CareerPlannerAgent(BaseAgent[CareerGoalInput, CareerPlanOutput]):
    async def run(self, inputs: CareerGoalInput) -> CareerPlanOutput:
        context_text = f"\nAdditional context:\n{inputs.context}" if inputs.context else ""

        user_prompt = CAREER_PLANNER_USER_PROMPT_TEMPLATE.format(
            goal_title=inputs.title,
            target_company=inputs.target_company,
            target_role=inputs.target_role,
            deadline=inputs.deadline,
            priority=inputs.priority,
            skills="Not yet uploaded",
            technologies="",
            experience_str="",
            projects_str="",
            context=context_text,
        )

        return await self._llm_call(
            system_prompt=CAREER_PLANNER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CareerPlanOutput,
        )


async def create_career_plan(
    title: str,
    target_company: str | None = None,
    target_role: str | None = None,
    deadline: str | None = None,
    priority: str = "medium",
    context: str | None = None,
    api_key: str | None = None,
) -> CareerPlanOutput:
    client = get_openai_client(api_key)
    agent = CareerPlannerAgent(AgentContext(openai_client=client))
    return await agent.run(CareerGoalInput(
        title=title,
        target_company=target_company,
        target_role=target_role,
        deadline=deadline,
        priority=priority,
        context=context,
    ))
