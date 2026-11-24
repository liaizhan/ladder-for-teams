"""Ladder for Teams: public functions.

Each function here is one tool an AI assistant can call (Claude, Cursor,
ChatGPT through MCP). Inputs and outputs are plain JSON-friendly types.

Flow for a team of any size:
1. get_questions()            the four questions of the Ladder method
2. build_member_ladder(...)   an employee answers privately, gets the ladder
3. weekly_step_for(...)       one concrete step for this week
4. check_in(...)              did the step happen? yes or no
5. team_report(...)           the lead sees themes and progress, never words
"""

import datetime
from collections import Counter
from typing import Dict, List, Optional

from .ladder import DISCLAIMER, InvalidLadder, build_ladder
from .safety import safety_notice
from .store import Store
from .themes import label_of, theme_of, weekly_step

#: A team report needs at least this many ladders, so nobody can be identified.
MIN_TEAM_FOR_REPORT = 3

#: A block theme is shown in the team report only if at least this many people share it.
MIN_MEMBERS_PER_THEME = 2

_store: Optional[Store] = None


def _db() -> Store:
    global _store
    if _store is None:
        _store = Store()
    return _store


def use_store(store: Store) -> None:
    """Swap the storage (tests, demos)."""
    global _store
    _store = store


def current_week(today: Optional[datetime.date] = None) -> str:
    year, week, _ = (today or datetime.date.today()).isocalendar()
    return f"{year}-W{week:02d}"


def get_questions() -> Dict:
    """Return the four questions of the Ladder method, in order, with hints."""
    return {
        "method": "The Ladder: your goal, the blocks between you and it, and the fears above it.",
        "questions": [
            {"field": "goal", "required": True,
             "question": "What is your measurable work goal?",
             "hint": "Something you can count, e.g. 'lead the Q1 release' or 'pass the AWS exam by March'."},
            {"field": "me", "required": True,
             "question": "Where are you now relative to this goal?",
             "hint": "One sentence."},
            {"field": "blocks", "required": True,
             "question": "Which phrases stand between you and the goal? Bottom up, 3 to 5.",
             "hint": "Phrases people say that you believe, e.g. 'Manager: you are not ready to lead'."},
            {"field": "fears", "required": False,
             "question": "What could go wrong if the goal comes true? Up to 5.",
             "hint": "Optional."},
        ],
        "disclaimer": DISCLAIMER,
    }


def build_member_ladder(team: str, member: str, goal: str, me: str,
                        blocks: List[str], fears: Optional[List[str]] = None) -> Dict:
    """Build one employee's ladder, save it privately and return the reading.

    The reading shows the steps bottom up, the nearest block (where work starts)
    and one step for this week. If the answers mention crisis or health, a care
    notice is returned instead and nothing is saved.
    """
    notice = safety_notice([goal, me, *blocks, *(fears or [])])
    if notice:
        return {"kind": "notice", "reason": notice["kind"], "message": notice["message"]}
    try:
        ladder = build_ladder(goal, me, blocks, fears)
    except InvalidLadder as error:
        return {"kind": "error", "message": str(error)}

    _db().save_ladder(team, member, ladder.to_dict(), [theme_of(b) for b in ladder.blocks])
    return {
        "kind": "reading",
        "steps": [step.__dict__ for step in ladder.steps()],
        "nearest_block": ladder.nearest_block,
        "fears_above_goal": len(ladder.fears),
        "this_week": weekly_step(ladder.nearest_block),
        "disclaimer": DISCLAIMER,
    }


def weekly_step_for(team: str, member: str) -> Dict:
    """Return this week's step for a member, aimed at their nearest block."""
    ladder = _db().get_ladder(team, member)
    if not ladder:
        return {"kind": "error", "message": "No ladder yet. Call build_member_ladder first."}
    return {"kind": "step", "week": current_week(), **weekly_step(ladder["blocks"][0])}


def check_in(team: str, member: str, done: bool, week: Optional[str] = None) -> Dict:
    """Record whether the member did this week's step."""
    week = week or current_week()
    _db().save_checkin(team, member, week, done)
    return {"kind": "checkin", "week": week, "done": done}


def team_report(team: str, week: Optional[str] = None) -> Dict:
    """Anonymous report for a team lead or HR.

    Shows which kinds of blocks the team shares and how many weekly steps
    were done. Never shows anyone's words. Needs at least 3 ladders.
    """
    themes_by_member = _db().team_themes(team)
    if len(themes_by_member) < MIN_TEAM_FOR_REPORT:
        return {"kind": "error",
                "message": f"A report needs at least {MIN_TEAM_FOR_REPORT} ladders so nobody can be identified."}
    week = week or current_week()
    counts = Counter(theme for themes in themes_by_member for theme in set(themes))
    checkins = _db().week_checkins(team, week)
    done = sum(checkins)
    shown = [(theme, count) for theme, count in counts.most_common() if count >= MIN_MEMBERS_PER_THEME]
    return {
        "kind": "report",
        "team": team,
        "week": week,
        "members": len(themes_by_member),
        "shared_blocks": [
            {"theme": theme, "label": label_of(theme), "members": count,
             "share": round(count / len(themes_by_member), 2)}
            for theme, count in shown
        ],
        "rare_blocks_hidden": len(counts) - len(shown),
        "steps_done": done,
        "steps_reported": len(checkins),
        "progress": round(done / len(themes_by_member), 2),
        "privacy": "Themes and counts only. Individual answers are never shown.",
    }
