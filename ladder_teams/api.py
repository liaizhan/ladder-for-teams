"""HTTP API for Ladder for Teams (FastAPI).

Synapse reads these endpoints and generates an MCP server from them, so an
AI assistant can run the Ladder with an employee and report to a team lead.

Run:  uvicorn ladder_teams.api:app --reload
"""

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from . import service

app = FastAPI(
    title="Ladder for Teams",
    description="The Ladder method by Aizhan Li for workplace goals: private ladders for employees, "
                "anonymous patterns for team leads. Self-reflection tool, not therapy.",
    version="0.1.0",
)


class LadderIn(BaseModel):
    team: str
    member: str
    goal: str
    me: str
    blocks: List[str]
    fears: Optional[List[str]] = None


class CheckInIn(BaseModel):
    team: str
    member: str
    done: bool
    week: Optional[str] = None


@app.get("/questions")
def get_questions() -> dict:
    """The four questions of the Ladder method: goal, where you are now, blocks, fears."""
    return service.get_questions()


@app.post("/ladders")
def build_member_ladder(body: LadderIn) -> dict:
    """Build an employee's ladder privately and return the reading with one step for this week."""
    return service.build_member_ladder(body.team, body.member, body.goal, body.me, body.blocks, body.fears)


@app.get("/teams/{team}/members/{member}/step")
def weekly_step_for(team: str, member: str) -> dict:
    """This week's step for one employee, aimed at the block nearest to them."""
    return service.weekly_step_for(team, member)


@app.post("/checkins")
def check_in(body: CheckInIn) -> dict:
    """Record whether the employee did this week's step."""
    return service.check_in(body.team, body.member, body.done, body.week)


@app.get("/teams/{team}/report")
def team_report(team: str, week: Optional[str] = None) -> dict:
    """Anonymous team report: shared kinds of blocks and weekly progress. Never shows anyone's words."""
    return service.team_report(team, week)
