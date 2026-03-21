"""
MCP server for interview prep content.
Serves problem/pattern/topic files — one item at a time, only what's needed.
"""
import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import DATA_DIR

mcp = FastMCP("interview-prep-content")

# ── Helpers ────────────────────────────────────────────────────────────────

def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path) as f:
        return json.load(f)

# ── MCP Tools ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_problem(id: str) -> dict[str, Any]:
    """
    Return a single algo problem by ID (e.g. "nc_015").
    Returns: title, url, difficulty, category, description, constraints,
             test_cases, thinking_questions, hints, follow_up_questions, optimal_time, optimal_space.
    """
    path = DATA_DIR / "algo" / f"{id}.json"
    return _read_json(path)


@mcp.tool()
def get_sql_problem(id: str) -> dict[str, Any]:
    """
    Return a single SQL problem by ID (e.g. "sql_001").
    Returns: id, title, difficulty, category, description, hints, key_concept, optimal_solution.
    Query problems also have: url, leetcode_id.
    Conceptual problems (is_conceptual: true) have no url — score on concept + clarity, not SQL code.
    """
    path = DATA_DIR / "sql" / f"{id}.json"
    return _read_json(path)


@mcp.tool()
def get_pattern(id: str) -> dict[str, Any]:
    """
    Return a single GoF/SOLID pattern by ID (e.g. "gof_001").
    Reads from gof/{id}.json — one file per pattern.
    Returns: name, description, core_concept, questions.
    """
    path = DATA_DIR / "gof" / f"{id}.json"
    return _read_json(path)


@mcp.tool()
def get_aiml_topic(id: str) -> dict[str, Any]:
    """
    Return a single AI/ML topic by ID (e.g. "ml_m01").
    Returns: title, summary, key_concepts, code_example, thinking_questions.
    """
    path = DATA_DIR / "aiml" / f"{id}.json"
    return _read_json(path)


@mcp.tool()
def get_behavioral_questions(ids: list[str]) -> list[dict[str, Any]]:
    """
    Return behavioral questions by ID list (e.g. ["bq_001", "bq_002"]).
    Reads behavioral.json once and returns the matching questions.
    """
    behavioral_file = DATA_DIR / "behavioral.json"
    data = _read_json(behavioral_file)

    # behavioral.json structure: {"behavioral": {"competencies": {name: {"questions": [...]}}}}
    competencies = data["behavioral"]["competencies"]
    all_questions = [q for comp in competencies.values() for q in comp["questions"]]
    id_set = set(ids)
    results = [q for q in all_questions if q.get("id") in id_set]

    if len(results) != len(ids):
        found = {q["id"] for q in results}
        missing = id_set - found
        raise ValueError(f"Behavioral question IDs not found: {missing}")

    # Return in requested order
    order = {id_: i for i, id_ in enumerate(ids)}
    return sorted(results, key=lambda q: order[q["id"]])


@mcp.tool()
def get_system_design(id: str) -> dict[str, Any]:
    """
    Return a single system design problem/topic by ID (e.g. "sd_c01").
    Reads system_design.json once and returns the matching item.
    """
    sd_file = DATA_DIR / "system_design.json"
    data = _read_json(sd_file)

    # system_design.json structure: {"system_design": {"levels": {name: {"topics"|"problems": [...]}}}}
    levels = data["system_design"]["levels"]
    for level in levels.values():
        items = level.get("problems", level.get("topics", []))
        for item in items:
            if item.get("id") == id:
                return item

    raise ValueError(f"System design item '{id}' not found in system_design.json")


@mcp.tool()
def get_item_titles(track: str, ids: list[str]) -> list[dict[str, str]]:
    """
    Return lightweight id→title mappings for a list of IDs — used by the greeting card.
    Does NOT return full problem content.

    Args:
        track: one of "algo", "sql", "gof", "aiml", "behavioral", "system_design", "nc_core", "ds"
        ids: list of item IDs

    Returns list of {"id": "nc_015", "title": "Two Sum II"}
    """
    results = []

    if track == "algo":
        for id_ in ids:
            try:
                d = _read_json(DATA_DIR / "algo" / f"{id_}.json")
                results.append({"id": id_, "title": d.get("title", id_)})
            except FileNotFoundError:
                results.append({"id": id_, "title": id_})

    elif track == "sql":
        for id_ in ids:
            try:
                d = _read_json(DATA_DIR / "sql" / f"{id_}.json")
                results.append({"id": id_, "title": d.get("title", id_)})
            except FileNotFoundError:
                results.append({"id": id_, "title": id_})

    elif track == "gof":
        for id_ in ids:
            try:
                d = _read_json(DATA_DIR / "gof" / f"{id_}.json")
                results.append({"id": id_, "title": d.get("name", id_)})
            except FileNotFoundError:
                results.append({"id": id_, "title": id_})

    elif track == "aiml":
        for id_ in ids:
            try:
                d = _read_json(DATA_DIR / "aiml" / f"{id_}.json")
                results.append({"id": id_, "title": d.get("title", id_)})
            except FileNotFoundError:
                results.append({"id": id_, "title": id_})

    elif track == "behavioral":
        data = _read_json(DATA_DIR / "behavioral.json")
        competencies = data["behavioral"]["competencies"]
        all_qs = {q["id"]: q.get("question", q["id"])[:60] + "…"
                  for comp in competencies.values() for q in comp["questions"]}
        for id_ in ids:
            results.append({"id": id_, "title": all_qs.get(id_, id_)})

    elif track == "system_design":
        data = _read_json(DATA_DIR / "system_design.json")
        levels = data["system_design"]["levels"]
        id_to_title: dict[str, str] = {}
        for level in levels.values():
            for item in level.get("problems", level.get("topics", [])):
                id_to_title[item["id"]] = item.get("title", item["id"])
        for id_ in ids:
            results.append({"id": id_, "title": id_to_title.get(id_, id_)})

    elif track == "nc_core":
        for id_ in ids:
            try:
                d = _read_json(DATA_DIR / "core" / f"{id_}.json")
                results.append({"id": id_, "title": d.get("title", id_)})
            except FileNotFoundError:
                results.append({"id": id_, "title": id_})

    elif track == "ds":
        data = _read_json(DATA_DIR / "data_structures.json")
        id_to_title = {c["id"]: c.get("title", c["id"]) for c in data["ds_concepts"]}
        for id_ in ids:
            results.append({"id": id_, "title": id_to_title.get(id_, id_)})

    else:
        results = [{"id": id_, "title": id_} for id_ in ids]

    return results


@mcp.tool()
def get_core_problem(id: str) -> dict[str, Any]:
    """
    Return a single NeetCode Core implementation problem by ID (e.g. "nc_core_dp01").
    Returns: id, trigger, title, difficulty, category, neetcode_url, description,
             key_concept, when_best, hints, optimal_solution, complexity.
    """
    path = DATA_DIR / "core" / f"{id}.json"
    return _read_json(path)


@mcp.tool()
def get_data_structure(id: str) -> dict[str, Any]:
    """
    Return a single data structure concept card by ID (e.g. "ds_a01").
    Reads data_structures.json and returns the matching entry.
    Returns: id, title, summary, key_concepts, time_complexity, when_to_use,
             common_patterns, code_example, thinking_questions.
    """
    ds_file = DATA_DIR / "data_structures.json"
    data = _read_json(ds_file)

    # data_structures.json structure: {"ds_concepts": [...]}
    concepts = data["ds_concepts"]
    for concept in concepts:
        if concept.get("id") == id:
            return concept

    raise ValueError(f"Data structure '{id}' not found in data_structures.json")


if __name__ == "__main__":
    mcp.run()
