"""Block themes and one small weekly step for each theme.

A block is a phrase a person believes ("Manager: we have no budget").
We sort it into a theme so a team lead can see patterns without reading
anyone's words, and so each person gets one concrete step for the week.
"""

import re
from typing import Dict, List

THEMES: Dict[str, Dict] = {
    "approval": {
        "label": "Waiting for someone's approval",
        "words": [r"manager", r"boss", r"lead", r"team", r"client", r"they", r"people", r"colleague",
                  r"mom", r"dad", r"family", r"husband", r"wife", r"won'?t let", r"approv", r"permission", r"sign[- ]?off", r"waiting for", r"security", r"legal"],
        "step": "Write down whose words this block is and ask that person one direct question about it this week.",
    },
    "time": {
        "label": "No time, too much load",
        "words": [r"time", r"busy", r"deadline", r"overload", r"too many", r"no capacity", r"later", r"tired"],
        "step": "Block 30 minutes in your calendar this week for the goal only, and protect it like a meeting.",
    },
    "money": {
        "label": "Money and resources",
        "words": [r"budget", r"money", r"cost", r"expensive", r"salary", r"funding", r"resources", r"pay"],
        "step": "Find out the real number: what exactly it costs and who decides. Write it down by Friday.",
    },
    "skill": {
        "label": "Not enough skills or knowledge",
        "words": [r"don'?t know how", r"skill", r"experience", r"learn", r"not qualified", r"junior",
                  r"technical", r"never done"],
        "step": "Pick the one skill this block is about and spend one hour on it with a person who already has it.",
    },
    "confidence": {
        "label": "Self-doubt",
        "words": [r"not good enough", r"can'?t", r"fail", r"who am i", r"impostor", r"stupid", r"afraid",
                  r"not ready", r"too old", r"too young", r"smarter", r"better than me", r"not smart"],
        "step": "Write three facts from your own work that argue with this phrase, and show one of them to a colleague.",
    },
}

OTHER = {
    "label": "Other",
    "step": "Name the smallest action that would make this block a little weaker, and do it before Friday.",
}


def theme_of(block: str) -> str:
    """Theme key for one block phrase; 'other' when no theme matches."""
    lowered = block.lower()
    best, best_hits = "other", 0
    for key, theme in THEMES.items():
        hits = sum(1 for pattern in theme["words"] if re.search(pattern, lowered))
        if hits > best_hits:
            best, best_hits = key, hits
    return best


def label_of(theme: str) -> str:
    return THEMES.get(theme, OTHER)["label"]


def weekly_step(block: str) -> Dict[str, str]:
    """One concrete step for this week, aimed at the nearest block."""
    theme = theme_of(block)
    return {"block": block, "theme": theme, "theme_label": label_of(theme),
            "step": THEMES.get(theme, OTHER)["step"]}


def all_theme_keys() -> List[str]:
    return list(THEMES) + ["other"]
