"""SQLite storage. One file, standard library only.

Privacy rule: a member's words (goal, blocks, fears) are stored only to
give that member their own ladder back. Team reports read themes and
counts, never the words.
"""

import json
import os
import sqlite3
import time
from typing import Dict, List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS ladders (
    team TEXT NOT NULL,
    member TEXT NOT NULL,
    ladder_json TEXT NOT NULL,
    themes_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    PRIMARY KEY (team, member)
);
CREATE TABLE IF NOT EXISTS checkins (
    team TEXT NOT NULL,
    member TEXT NOT NULL,
    week TEXT NOT NULL,
    done INTEGER NOT NULL,
    PRIMARY KEY (team, member, week)
);
"""


def default_path() -> str:
    return os.environ.get("LADDER_TEAMS_DB", "ladder_teams.db")


class Store:
    def __init__(self, path: Optional[str] = None):
        self.conn = sqlite3.connect(path or default_path())
        self.conn.executescript(SCHEMA)

    def save_ladder(self, team: str, member: str, ladder: Dict, themes: List[str]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO ladders VALUES (?, ?, ?, ?, ?)",
            (team, member, json.dumps(ladder), json.dumps(themes), time.time()),
        )
        self.conn.commit()

    def get_ladder(self, team: str, member: str) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT ladder_json FROM ladders WHERE team = ? AND member = ?", (team, member)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def team_themes(self, team: str) -> List[List[str]]:
        rows = self.conn.execute("SELECT themes_json FROM ladders WHERE team = ?", (team,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def save_checkin(self, team: str, member: str, week: str, done: bool) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO checkins VALUES (?, ?, ?, ?)", (team, member, week, int(done))
        )
        self.conn.commit()

    def week_checkins(self, team: str, week: str) -> List[bool]:
        rows = self.conn.execute(
            "SELECT done FROM checkins WHERE team = ? AND week = ?", (team, week)
        ).fetchall()
        return [bool(row[0]) for row in rows]
