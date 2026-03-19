"""
Shared fixtures for nanogrindv2 tests.
Sets INTERVIEW_PREP_DATA to a temp directory so tests never touch real data.
"""
import json
import os
import pytest
from pathlib import Path


FIXTURE_PROGRESS = {
    "schema_version": "2.0",
    "curriculum_version": "2.0",
    "start_date": "2026-03-08",
    "last_active_date": "2026-03-16",
    "streak_days": 6,
    "rest_days": ["sunday"],
    "completed_problem_ids": [
        "nc_001","nc_002","nc_003","nc_004","nc_005",
        "nc_006","nc_007","nc_008","nc_009","nc_010",
        "nc_011","nc_012","nc_013","nc_014",
    ],
    "skipped_problem_ids": [],
    "completed_pattern_ids": [],
    "completed_concept_ids": [],
    "completed_design_ids": [],
    "completed_behavioral_ids": [],
    "completed_sql_ids": [],
    "completed_core_ids": [],
    "completed_ds_ids": [],
    "postponed_problem_ids": [],
    "postponed_pattern_ids": ["gof_001"],
    "postponed_concept_ids": ["ml_m01"],
    "postponed_behavioral_ids": [],
    "postponed_sql_ids": ["sql_001", "sql_002"],
    "postponed_design_ids": [],
    "postponed_core_ids": [],
    "postponed_ds_ids": [],
    "in_progress": None,
    "active_session": None,
    "week_start": "2026-03-16",
    "week_completions": {"algo": 0, "sql": 0, "gof": 0, "aiml": 0},
    "quiz_today_count": 0,
    "quiz_today_date": None,
    "stats": {
        "total_problems_solved": 14,
        "total_design_mocks": 0,
        "total_pattern_sessions": 0,
        "total_reviews": 0,
        "total_behavioral_sessions": 0,
        "total_sql_solved": 0,
        "total_aiml_sessions": 0,
    },
}

FIXTURE_ATTEMPTS = {
    "schema_version": "1.0",
    "attempts": [],
}

FIXTURE_REVIEW_QUEUE = {
    "items": [],
}

FIXTURE_WEAK_AREAS = {
    "schema_version": "1.0",
    "last_computed": None,
    "by_pattern_tag": {},
}

# Minimal algo problem file for tests that need pattern_tags
FIXTURE_GOF_PATTERNS = [
    {"id": "gof_001", "name": "Singleton", "category": "Creational", "questions": ["Q1", "Q2", "Q3"]},
    {"id": "gof_002", "name": "Factory Method", "category": "Creational", "questions": ["Q1", "Q2", "Q3"]},
    {"id": "gof_003", "name": "Abstract Factory", "category": "Creational", "questions": ["Q1", "Q2"]},
]

FIXTURE_ALGO_NC015 = {
    "id": "nc_015",
    "title": "Best Time to Buy and Sell Stock",
    "difficulty": "easy",
    "category": "Sliding Window",
    "pattern_tags": ["sliding_window", "arrays"],
    "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
    "description": "...",
    "test_cases": [{"input": [7,1,5,3,6,4], "output": 5}],
    "thinking_questions": ["What do you need to track?"],
    "hints": ["Track min price seen so far"],
    "optimal_time": "O(n)",
    "optimal_space": "O(1)",
}


def _reload_server(data_dir: Path):
    """Reload config + progress_server so they pick up the new INTERVIEW_PREP_DATA env."""
    import importlib
    import servers.config as cfg
    importlib.reload(cfg)
    import servers.progress_server as ps
    importlib.reload(ps)
    return ps


@pytest.fixture()
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Create a temp data directory with clean fixture files.
    Sets INTERVIEW_PREP_DATA so servers use this dir, not the real VM path.
    """
    # Core data files
    (tmp_path / "progress.json").write_text(json.dumps(FIXTURE_PROGRESS, indent=2))
    (tmp_path / "attempts.json").write_text(json.dumps(FIXTURE_ATTEMPTS, indent=2))
    (tmp_path / "review_queue.json").write_text(json.dumps(FIXTURE_REVIEW_QUEUE, indent=2))
    (tmp_path / "weak_areas.json").write_text(json.dumps(FIXTURE_WEAK_AREAS, indent=2))

    # Stub algo problem dir with nc_015 so log_attempt can look up pattern_tags
    algo_dir = tmp_path / "algo"
    algo_dir.mkdir()
    (algo_dir / "nc_015.json").write_text(json.dumps(FIXTURE_ALGO_NC015, indent=2))

    # Stub gof/ dir for evening drill tests
    gof_dir = tmp_path / "gof"
    gof_dir.mkdir()
    for p in FIXTURE_GOF_PATTERNS:
        (gof_dir / f"{p['id']}.json").write_text(json.dumps(p, indent=2))

    monkeypatch.setenv("INTERVIEW_PREP_DATA", str(tmp_path))
    _reload_server(tmp_path)

    return tmp_path


@pytest.fixture()
def progress_file(data_dir: Path) -> Path:
    return data_dir / "progress.json"


@pytest.fixture()
def attempts_file(data_dir: Path) -> Path:
    return data_dir / "attempts.json"


@pytest.fixture()
def review_file(data_dir: Path) -> Path:
    return data_dir / "review_queue.json"


def read_progress(data_dir: Path) -> dict:
    return json.loads((data_dir / "progress.json").read_text())

def read_attempts(data_dir: Path) -> dict:
    return json.loads((data_dir / "attempts.json").read_text())

def read_review_queue(data_dir: Path) -> dict:
    return json.loads((data_dir / "review_queue.json").read_text())
