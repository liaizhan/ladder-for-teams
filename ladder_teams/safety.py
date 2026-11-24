"""Safety first: some answers must not be analysed as a ladder.

If a person writes about self-harm, violence or crisis, we stop and show
where to get help. If they write about illnesses and symptoms, we say the
ladder does not analyse health and suggest a doctor. Simple word lists on
purpose: predictable, testable, no model in the loop.
"""

import re
from typing import Iterable, Optional

CRISIS_WORDS = [
    r"suicid", r"kill myself", r"end my life", r"self[- ]?harm", r"hurt myself",
    r"don'?t want to live", r"abuse", r"he hits me", r"she hits me", r"violence",
    r"суицид", r"покончить с собой", r"не хочу жить", r"бьёт меня", r"бьет меня", r"насили",
]

HEALTH_WORDS = [
    r"diagnos", r"symptom", r"cancer", r"tumou?r", r"diabet", r"migraine", r"chronic pain",
    r"medication", r"pills", r"blood pressure", r"panic attack",
    r"диагноз", r"симптом", r"таблетк", r"давлени", r"опухол", r"диабет",
]

HELP_TEXT = (
    "It sounds like you may be going through something serious. The Ladder is not the right tool "
    "for this. Please contact local emergency services or a crisis line now, or talk to someone you trust."
)

HEALTH_TEXT = (
    "The Ladder does not analyse illnesses, symptoms or treatment. For health questions, please talk "
    "to a doctor. You can still build a ladder for a work goal without health details."
)


def _matches(patterns: Iterable[str], text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def safety_notice(texts: Iterable[str]) -> Optional[dict]:
    """Return a notice dict if the answers need care instead of analysis, else None."""
    joined = "\n".join(texts)
    if _matches(CRISIS_WORDS, joined):
        return {"kind": "crisis", "message": HELP_TEXT}
    if _matches(HEALTH_WORDS, joined):
        return {"kind": "health", "message": HEALTH_TEXT}
    return None
