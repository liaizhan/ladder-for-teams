"""Seed two teammates before recording the demo, so the team report can open.

A report needs at least 3 ladders. On camera we build the third one live.

Run from the project folder, with the same LADDER_TEAMS_DB the API uses:
    .venv/bin/python -m scripts.seed_demo
"""

from ladder_teams import service

TEAM = "payments"

TEAMMATES = [
    ("arman", "Ship the new checkout by February",
     "Backend engineer, checkout half done",
     ["Waiting for approval from security", "No time, on-call every second week",
      "I'm not good enough at frontend"]),
    ("madina", "Pass the AWS Solutions Architect exam by March",
     "Studied 2 of 12 modules",
     ["No time after work", "The course is too expensive", "Others are smarter than me"]),
]

for member, goal, me, blocks in TEAMMATES:
    service.build_member_ladder(TEAM, member, goal, me, blocks)
service.check_in(TEAM, "arman", True)
service.check_in(TEAM, "madina", False)
print(f"Seeded {len(TEAMMATES)} ladders in team '{TEAM}'.")
