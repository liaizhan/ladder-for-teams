"""Call the Synapse-generated MCP server over stdio, the way Claude Desktop does.

Start the API first (same LADDER_TEAMS_DB as the seed):
    .venv/bin/uvicorn ladder_teams.api:app --port 8000
    .venv/bin/python -m scripts.seed_demo
Then:
    .venv/bin/python -m scripts.mcp_demo_client
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.environ.get("ENDPOINT_BASE_URL", "http://127.0.0.1:8000")

CALLS = [
    ("build_member_ladder", {
        "team": "payments", "member": "dana",
        "goal": "Lead the Q1 release", "me": "Senior engineer, never led a release",
        "blocks": ["Manager: you are not ready to lead",
                   "No time, too many tickets this sprint",
                   "I don't know how to run a planning meeting"],
        "fears": ["Others will expect more from me"]}),
    ("weekly_step_for", {"team": "payments", "member": "dana"}),
    ("check_in", {"team": "payments", "member": "dana", "done": True}),
    ("team_report", {"team": "payments"}),
    ("build_member_ladder", {
        "team": "payments", "member": "eli", "goal": "Get promoted", "me": "Mid-level",
        "blocks": ["I don't want to live like this", "No time", "No budget"]}),
]


async def main() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "synapse_auto_server.py")],
        env={"ENDPOINT_BASE_URL": BASE_URL},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [tool.name for tool in tools.tools])
            for name, args in CALLS:
                result = await session.call_tool(name, args)
                print(f"\n>>> {name} {json.dumps(args)}")
                print("<<<", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
