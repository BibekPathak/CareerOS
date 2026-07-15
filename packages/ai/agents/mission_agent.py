from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.mission import (
    MISSION_COMMANDER_SYSTEM_PROMPT,
    MISSION_COMMANDER_USER_PROMPT_TEMPLATE,
)
from pydantic import BaseModel


class MissionAction(BaseModel):
    type: str
    target: str
    detail: str
    deadline: str
    urgency: str


class GoalMission(BaseModel):
    goal_title: str
    actions: list[MissionAction]
    focus: str
    progress: str


class TodaysMission(BaseModel):
    goals: list[GoalMission]
    summary_stats: dict = {}


class MissionInput(BaseModel):
    goals: list[dict]
    follow_ups: list[dict]
    recent_activity: list[dict]
    stats: dict | None = None


class MissionCommanderAgent(BaseAgent[MissionInput, TodaysMission]):
    async def run(self, inputs: MissionInput) -> TodaysMission:
        def fmt(items: list[dict]) -> str:
            if not items:
                return "None"
            return "\n".join(
                f"  - {i.get('title', '')}: {i.get('description', '')} [{i.get('urgency', 'medium')}]"
                for i in items
            )

        stats_text = ""
        if inputs.stats:
            stats_text = "\n".join(f"  {k}: {v}" for k, v in inputs.stats.items())

        user_prompt = MISSION_COMMANDER_USER_PROMPT_TEMPLATE.format(
            goals_str=fmt(inputs.goals),
            follow_ups_str=fmt(inputs.follow_ups),
            activity_str=fmt(inputs.recent_activity),
            stats_str=stats_text or "No stats available",
        )

        return await self._llm_call(
            system_prompt=MISSION_COMMANDER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=TodaysMission,
        )


async def generate_todays_mission(
    goals: list[dict],
    follow_ups: list[dict],
    recent_activity: list[dict],
    stats: dict | None = None,
    api_key: str | None = None,
) -> TodaysMission:
    client = get_openai_client(api_key)
    agent = MissionCommanderAgent(AgentContext(openai_client=client))
    return await agent.run(MissionInput(
        goals=goals,
        follow_ups=follow_ups,
        recent_activity=recent_activity,
        stats=stats,
    ))
