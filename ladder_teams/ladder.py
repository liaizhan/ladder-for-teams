"""The Ladder method: one person's goal, laid out as a ladder of steps.

The ladder is read from the bottom up:

    fears        (what might happen if the goal comes true)
    GOAL
    blocks       (phrases people say that the person believes)
    ME           (where the person is now, always step 1)

Work starts with the block nearest to "me". Method by Aizhan Li,
author of the Ladder method (108psy.com). This is a self-reflection tool,
not therapy and not medical advice.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

MIN_BLOCKS = 3
MAX_BLOCKS = 5
MAX_FEARS = 5
MAX_CHARS = 300

DISCLAIMER = (
    "Self-reflection tool based on the Ladder method by Aizhan Li. "
    "It is not therapy, diagnosis or medical advice."
)


class InvalidLadder(ValueError):
    """The answers are not enough to build a ladder."""


@dataclass
class Step:
    number: int
    zone: str  # "me" | "block" | "goal" | "fear"
    text: str


@dataclass
class Ladder:
    goal: str
    me: str
    blocks: List[str]
    fears: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Raise InvalidLadder with a human-readable reason if answers are incomplete."""
        if not self.goal.strip():
            raise InvalidLadder("Write a measurable goal, for example 'ship the billing API by 1 March'.")
        if not self.me.strip():
            raise InvalidLadder("Describe in one sentence where you are now relative to the goal.")
        if not MIN_BLOCKS <= len(self.blocks) <= MAX_BLOCKS:
            raise InvalidLadder(
                f"List {MIN_BLOCKS} to {MAX_BLOCKS} blocks, bottom up: short phrases people say, "
                "for example 'Manager: we have no budget for this'."
            )
        if len(self.fears) > MAX_FEARS:
            raise InvalidLadder(f"List at most {MAX_FEARS} fears.")
        for text in [self.goal, self.me, *self.blocks, *self.fears]:
            if len(text) > MAX_CHARS:
                raise InvalidLadder(f"Keep every answer under {MAX_CHARS} characters.")

    def steps(self) -> List[Step]:
        """All steps bottom up: me, blocks, goal, fears."""
        steps = [Step(1, "me", self.me)]
        for block in self.blocks:
            steps.append(Step(len(steps) + 1, "block", block))
        steps.append(Step(len(steps) + 1, "goal", self.goal))
        for fear in self.fears:
            steps.append(Step(len(steps) + 1, "fear", fear))
        return steps

    @property
    def nearest_block(self) -> str:
        return self.blocks[0]

    def to_dict(self) -> Dict:
        return asdict(self)


def build_ladder(goal: str, me: str, blocks: List[str], fears: Optional[List[str]] = None) -> Ladder:
    """Clean the answers, build a ladder and validate it."""
    ladder = Ladder(
        goal=goal.strip(),
        me=me.strip(),
        blocks=[b.strip() for b in blocks if b and b.strip()],
        fears=[f.strip() for f in (fears or []) if f and f.strip()],
    )
    ladder.validate()
    return ladder
