"""
Integration tests using Claude API.
Verifies that an agent using the MCP tools behaves correctly end-to-end.
Requires ANTHROPIC_API_KEY environment variable.
"""
import json
import os
import pytest
import anthropic
from pathlib import Path
from .conftest import read_progress, FIXTURE_PROGRESS


SKIP_REASON = "ANTHROPIC_API_KEY not set"
requires_api = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason=SKIP_REASON,
)

MODEL = "claude-haiku-4-5-20251001"

# ── Tool definitions (mirrors our MCP servers) ────────────────────────────

def make_tools(ps, cs=None) -> list[dict]:
    """Build Claude tool definitions from our server functions."""
    tools = [
        {
            "name": "get_progress",
            "description": "Return current progress summary — streak, stats, in_progress item.",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_next_items",
            "description": (
                "Return next N items for a track in correct queue order. "
                "Postponed items always come first. "
                "Tracks: algo, sql, gof, aiml, behavioral, system_design."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "track": {"type": "string"},
                    "n":     {"type": "integer", "default": 1},
                },
                "required": ["track"],
            },
        },
        {
            "name": "set_in_progress",
            "description": "Mark an item as currently in progress.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "track": {"type": "string"},
                    "id":    {"type": "string"},
                },
                "required": ["track", "id"],
            },
        },
        {
            "name": "add_completed",
            "description": "Mark an item as completed. Updates stats and streak. Only touches the 3 relevant fields.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "track": {"type": "string"},
                    "id":    {"type": "string"},
                },
                "required": ["track", "id"],
            },
        },
        {
            "name": "add_postponed",
            "description": "Add item to postponed list (max 3 per track).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "track": {"type": "string"},
                    "id":    {"type": "string"},
                },
                "required": ["track", "id"],
            },
        },
        {
            "name": "get_problem",
            "description": "Return a single algo problem by ID (e.g. nc_015).",
            "input_schema": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
        {
            "name": "get_sql_problem",
            "description": "Return a single SQL problem by ID (e.g. sql_001).",
            "input_schema": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
    ]
    if cs:
        tools.append({
            "name": "get_pattern",
            "description": "Return a single GoF pattern by ID.",
            "input_schema": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        })
    return tools


def run_agent(system: str, user_message: str, ps, cs=None, max_rounds: int = 10):
    """
    Run a simple agent loop with Claude.
    Returns (messages, tool_call_names) for assertion.
    """
    client = anthropic.Anthropic()
    tools = make_tools(ps, cs)
    messages = [{"role": "user", "content": user_message}]
    tool_call_names = []

    for _ in range(max_rounds):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system,
            tools=tools,
            messages=messages,
        )

        # Collect tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_call_names.append(block.name)
                result = _dispatch_tool(block.name, block.input, ps, cs)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        # Add assistant message
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return messages, tool_call_names


def _dispatch_tool(name: str, inputs: dict, ps, cs):
    """Route tool call to the right server function."""
    if name == "get_progress":
        return ps.get_progress()
    elif name == "get_next_items":
        return ps.get_next_items(**inputs)
    elif name == "set_in_progress":
        return ps.set_in_progress(**inputs)
    elif name == "add_completed":
        return ps.add_completed(**inputs)
    elif name == "add_postponed":
        return ps.add_postponed(**inputs)
    elif name == "get_problem" and cs:
        return cs.get_problem(**inputs)
    elif name == "get_sql_problem" and cs:
        return cs.get_sql_problem(**inputs)
    elif name == "get_pattern" and cs:
        return cs.get_pattern(**inputs)
    return {"error": f"Unknown tool: {name}"}


GREETING_SYSTEM = """
You are an interview prep tutor for Mayu.
When greeted, show today's schedule card using these tools:
1. Call get_progress to get streak and stats.
2. Call get_next_items for each track: algo (n=3), sql (n=2), gof (n=1), aiml (n=1).
3. Output a plain text card showing today's items. Prefix postponed items with 🔒.
Do not read any content files during greeting — just show IDs and track names.
"""

ALGO_SYSTEM = """
You are an interview prep tutor.
When the user says "algo", start an algo session:
1. Call get_next_items("algo", n=1) to find the next problem.
2. Call set_in_progress with the track and ID.
3. Call get_problem with the ID to get problem details.
4. Present the problem (title, URL, first test case, thinking questions).
5. Wait for the user's solution attempt.
"""


# ── Tests ──────────────────────────────────────────────────────────────────

@requires_api
def test_greeting_calls_correct_tools(data_dir):
    ps = get_server_module(data_dir)
    _, tool_calls = run_agent(GREETING_SYSTEM, "hello!", ps)

    assert "get_progress" in tool_calls
    # Must call get_next_items for each track
    next_item_calls = [t for t in tool_calls if t == "get_next_items"]
    assert len(next_item_calls) >= 4  # algo, sql, gof, aiml


@requires_api
def test_greeting_no_content_file_reads(data_dir):
    ps = get_server_module(data_dir)
    _, tool_calls = run_agent(GREETING_SYSTEM, "hello!", ps)

    # Should NOT call content tools during greeting
    assert "get_problem" not in tool_calls
    assert "get_sql_problem" not in tool_calls
    assert "get_aiml_topic" not in tool_calls
    assert "get_pattern" not in tool_calls


@requires_api
def test_algo_session_correct_problem(data_dir):
    """Agent should present nc_015 (first uncompleted after nc_001–nc_014)."""
    from servers import content_server as cs_module
    ps = get_server_module(data_dir)

    # Point content server at real data for this test
    real_data = os.environ.get(
        "INTERVIEW_PREP_DATA_REAL",
        str(Path(__file__).parent.parent.parent /
            "nanogrind/workspace/interview-prep/data")
    )
    os.environ["INTERVIEW_PREP_DATA"] = real_data
    import importlib
    import servers.config as cfg
    importlib.reload(cfg)
    import servers.content_server as cs
    importlib.reload(cs)

    _, tool_calls = run_agent(ALGO_SYSTEM, "algo", ps, cs)

    assert "get_next_items" in tool_calls
    assert "set_in_progress" in tool_calls
    assert "get_problem" in tool_calls

    # in_progress should be set to nc_015
    ip = ps.get_in_progress()
    assert ip is not None
    assert ip["id"] == "nc_015"
    assert ip["track"] == "algo"


@requires_api
def test_sql_postponed_presented_first(data_dir):
    """SQL session should present sql_001 and sql_002 (postponed), not sql_003."""
    ps = get_server_module(data_dir)

    SQL_SYSTEM = """
    You are an interview prep tutor.
    When user says "sql", call get_next_items("sql", n=2) to get the SQL problems.
    The first item returned is the first problem to present.
    Call set_in_progress for it.
    """

    _, tool_calls = run_agent(SQL_SYSTEM, "sql", ps)

    assert "get_next_items" in tool_calls
    assert "set_in_progress" in tool_calls

    ip = ps.get_in_progress()
    assert ip is not None
    assert ip["id"] == "sql_001"  # postponed item, not sql_003


@requires_api
def test_add_completed_does_not_corrupt(data_dir):
    """Completing an item via agent tool call must not wipe other fields."""
    ps = get_server_module(data_dir)

    COMPLETE_SYSTEM = """
    Complete the item nc_015 in the algo track by calling add_completed.
    """

    run_agent(COMPLETE_SYSTEM, "mark nc_015 done", ps)
    data = read_progress(data_dir)

    assert "nc_015" in data["completed_problem_ids"]
    # Other fields untouched
    assert data["postponed_sql_ids"] == ["sql_001", "sql_002"]
    assert data["postponed_pattern_ids"] == ["gof_001"]
    assert data["postponed_concept_ids"] == ["ml_m01"]
    assert data["stats"]["total_sql_solved"] == 0


def get_server_module(data_dir):
    os.environ["INTERVIEW_PREP_DATA"] = str(data_dir)
    import importlib
    import servers.config as cfg
    importlib.reload(cfg)
    import servers.progress_server as ps
    importlib.reload(ps)
    return ps
