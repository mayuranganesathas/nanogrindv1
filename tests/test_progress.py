"""Unit tests for progress_server tools."""
import json
import os
import pytest
from datetime import date, timedelta
from pathlib import Path
from .conftest import read_progress, read_attempts, read_review_queue


# ── Helpers ────────────────────────────────────────────────────────────────

def get_server(data_dir):
    """Import progress server functions after env is patched."""
    os.environ["INTERVIEW_PREP_DATA"] = str(data_dir)
    import importlib
    import servers.config as cfg
    importlib.reload(cfg)
    import servers.progress_server as ps
    importlib.reload(ps)
    return ps


# ── get_progress ───────────────────────────────────────────────────────────

def test_get_progress_returns_summary(data_dir):
    ps = get_server(data_dir)
    result = ps.get_progress()
    assert result["streak_days"] == 6
    assert result["start_date"] == "2026-03-08"
    assert result["in_progress"] is None
    assert "total_problems_solved" in result["stats"]
    assert "completed_problem_ids" not in result  # full lists not exposed


def test_get_progress_includes_completed_counts(data_dir):
    ps = get_server(data_dir)
    result = ps.get_progress()
    counts = result["completed_counts"]
    assert counts["algo"] == 14
    assert counts["sql"] == 0
    assert counts["gof"] == 0


# ── get_next_items ─────────────────────────────────────────────────────────

def test_algo_next_skips_completed(data_dir):
    ps = get_server(data_dir)
    result = ps.get_next_items("algo", n=3)
    assert len(result) == 3
    assert result[0]["id"] == "nc_015"
    assert result[1]["id"] == "nc_016"
    assert result[2]["id"] == "nc_017"
    assert not any(r["postponed"] for r in result)


def test_sql_postponed_come_first(data_dir):
    ps = get_server(data_dir)
    result = ps.get_next_items("sql", n=2)
    assert result[0] == {"id": "sql_001", "postponed": True}
    assert result[1] == {"id": "sql_002", "postponed": True}


def test_sql_postponed_then_new(data_dir):
    ps = get_server(data_dir)
    result = ps.get_next_items("sql", n=3)
    assert result[0]["id"] == "sql_001"
    assert result[0]["postponed"] is True
    assert result[1]["id"] == "sql_002"
    assert result[1]["postponed"] is True
    assert result[2]["id"] == "sql_003"
    assert result[2]["postponed"] is False


def test_gof_postponed_comes_first(data_dir):
    ps = get_server(data_dir)
    result = ps.get_next_items("gof", n=1)
    assert result[0] == {"id": "gof_001", "postponed": True}


def test_aiml_postponed_comes_first(data_dir):
    ps = get_server(data_dir)
    result = ps.get_next_items("aiml", n=1)
    assert result[0] == {"id": "ml_m01", "postponed": True}


def test_aiml_respects_phase_order(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("aiml", "ml_m01")
    result = ps.get_next_items("aiml", n=1)
    assert result[0]["id"] == "ml_m02"


def test_get_next_items_invalid_track(data_dir):
    ps = get_server(data_dir)
    with pytest.raises(ValueError, match="Unknown track"):
        ps.get_next_items("bogus")


# ── add_completed ──────────────────────────────────────────────────────────

def test_add_completed_appends_id(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    data = read_progress(data_dir)
    assert "nc_015" in data["completed_problem_ids"]


def test_add_completed_increments_stat(data_dir):
    ps = get_server(data_dir)
    before = read_progress(data_dir)["stats"]["total_problems_solved"]
    ps.add_completed("algo", "nc_015")
    after = read_progress(data_dir)["stats"]["total_problems_solved"]
    assert after == before + 1


def test_add_completed_does_not_touch_other_fields(data_dir):
    ps = get_server(data_dir)
    before = read_progress(data_dir)
    ps.add_completed("algo", "nc_015")
    after = read_progress(data_dir)
    assert after["completed_sql_ids"] == before["completed_sql_ids"]
    assert after["completed_pattern_ids"] == before["completed_pattern_ids"]
    assert after["completed_concept_ids"] == before["completed_concept_ids"]
    assert after["postponed_sql_ids"] == before["postponed_sql_ids"]
    assert after["postponed_pattern_ids"] == before["postponed_pattern_ids"]
    assert after["postponed_concept_ids"] == before["postponed_concept_ids"]
    assert after["stats"]["total_sql_solved"] == before["stats"]["total_sql_solved"]
    assert after["stats"]["total_pattern_sessions"] == before["stats"]["total_pattern_sessions"]


def test_add_completed_removes_from_postponed(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("gof", "gof_001")
    data = read_progress(data_dir)
    assert "gof_001" not in data["postponed_pattern_ids"]
    assert "gof_001" in data["completed_pattern_ids"]


def test_add_completed_clears_in_progress(data_dir):
    ps = get_server(data_dir)
    ps.set_in_progress("algo", "nc_015")
    ps.add_completed("algo", "nc_015")
    data = read_progress(data_dir)
    assert data["in_progress"] is None


def test_add_completed_idempotent(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    ps.add_completed("algo", "nc_015")
    data = read_progress(data_dir)
    assert data["completed_problem_ids"].count("nc_015") == 1
    assert data["stats"]["total_problems_solved"] == 15


# ── add_postponed ──────────────────────────────────────────────────────────

def test_add_postponed(data_dir):
    ps = get_server(data_dir)
    result = ps.add_postponed("algo", "nc_020")
    assert result["ok"] == "true"
    data = read_progress(data_dir)
    assert "nc_020" in data["postponed_problem_ids"]


def test_add_postponed_enforces_limit(data_dir):
    ps = get_server(data_dir)
    ps.add_postponed("algo", "nc_015")
    ps.add_postponed("algo", "nc_016")
    ps.add_postponed("algo", "nc_017")
    result = ps.add_postponed("algo", "nc_018")
    assert result["ok"] == "false"
    assert "Backlog full" in result["error"]


def test_add_postponed_idempotent(data_dir):
    ps = get_server(data_dir)
    ps.add_postponed("algo", "nc_015")
    result = ps.add_postponed("algo", "nc_015")
    assert result["ok"] == "true"
    data = read_progress(data_dir)
    assert data["postponed_problem_ids"].count("nc_015") == 1


def test_postpone_limit_is_per_track(data_dir):
    ps = get_server(data_dir)
    ps.add_postponed("algo", "nc_015")
    ps.add_postponed("algo", "nc_016")
    ps.add_postponed("algo", "nc_017")
    result = ps.add_postponed("sql", "sql_003")
    assert result["ok"] == "true"


# ── remove_postponed ───────────────────────────────────────────────────────

def test_remove_postponed(data_dir):
    ps = get_server(data_dir)
    ps.remove_postponed("sql", "sql_001")
    data = read_progress(data_dir)
    assert "sql_001" not in data["postponed_sql_ids"]
    assert "sql_002" in data["postponed_sql_ids"]


def test_remove_postponed_not_present(data_dir):
    ps = get_server(data_dir)
    result = ps.remove_postponed("sql", "sql_099")
    assert result["ok"] == "true"


# ── set_in_progress / get_in_progress ─────────────────────────────────────

def test_set_and_get_in_progress(data_dir):
    ps = get_server(data_dir)
    ps.set_in_progress("algo", "nc_015")
    result = ps.get_in_progress()
    assert result["track"] == "algo"
    assert result["id"] == "nc_015"
    assert "start_time" in result  # now includes start_time


def test_get_in_progress_null_by_default(data_dir):
    ps = get_server(data_dir)
    assert ps.get_in_progress() is None


# ── get_next_items after completions ──────────────────────────────────────

def test_next_items_updates_after_completion(data_dir):
    ps = get_server(data_dir)
    assert ps.get_next_items("algo", 1)[0]["id"] == "nc_015"
    ps.add_completed("algo", "nc_015")
    assert ps.get_next_items("algo", 1)[0]["id"] == "nc_016"


# ── log_attempt ────────────────────────────────────────────────────────────

def test_log_attempt_writes_to_attempts_file(data_dir):
    ps = get_server(data_dir)
    scores = {"correctness": 4, "efficiency": 3, "code_quality": 4, "pattern_recognition": 3, "explain_back": 4}
    result = ps.log_attempt("algo", "nc_015", scores=scores, solution="function f(){}")
    assert result["composite_score"] == pytest.approx(3.6)
    data = read_attempts(data_dir)
    assert len(data["attempts"]) == 1
    attempt = data["attempts"][0]
    assert attempt["item_id"] == "nc_015"
    assert attempt["track"] == "algo"
    assert attempt["composite_score"] == pytest.approx(3.6)
    assert attempt["solution"] == "function f(){}"


def test_log_attempt_captures_pattern_tags(data_dir):
    ps = get_server(data_dir)
    # nc_015.json exists in fixture with pattern_tags = ["sliding_window", "arrays"]
    ps.log_attempt("algo", "nc_015", scores={"correctness": 3, "efficiency": 3, "code_quality": 3, "pattern_recognition": 3, "explain_back": 3})
    data = read_attempts(data_dir)
    assert "sliding_window" in data["attempts"][0]["pattern_tags"]
    assert "arrays" in data["attempts"][0]["pattern_tags"]


def test_log_attempt_missing_file_uses_empty_tags(data_dir):
    ps = get_server(data_dir)
    # nc_099.json does not exist — should not raise, just use empty tags
    result = ps.log_attempt("algo", "nc_099", scores={"correctness": 2, "efficiency": 2, "code_quality": 2, "pattern_recognition": 2, "explain_back": 2})
    assert result["composite_score"] == pytest.approx(2.0)
    data = read_attempts(data_dir)
    assert data["attempts"][0]["pattern_tags"] == []


def test_log_attempt_schedules_review_for_low_score(data_dir):
    ps = get_server(data_dir)
    scores = {"correctness": 2, "efficiency": 2, "code_quality": 2, "pattern_recognition": 2, "explain_back": 2}
    result = ps.log_attempt("algo", "nc_015", scores=scores)
    assert result["composite_score"] == pytest.approx(2.0)
    assert result["review_scheduled"] is not None
    # Score 2 → 2 days from today
    expected = (date.today() + timedelta(days=2)).isoformat()
    assert result["review_scheduled"] == expected
    rq = read_review_queue(data_dir)
    assert len(rq["items"]) == 1
    assert rq["items"][0]["item_id"] == "nc_015"
    assert rq["items"][0]["scheduled_date"] == expected


def test_log_attempt_no_review_for_score_5(data_dir):
    ps = get_server(data_dir)
    scores = {"correctness": 5, "efficiency": 5, "code_quality": 5, "pattern_recognition": 5, "explain_back": 5}
    result = ps.log_attempt("algo", "nc_015", scores=scores)
    assert result["composite_score"] == pytest.approx(5.0)
    assert result["review_scheduled"] is None
    rq = read_review_queue(data_dir)
    assert len(rq["items"]) == 0


def test_log_attempt_review_delays_by_score(data_dir):
    ps = get_server(data_dir)
    cases = [(1, 1), (2, 2), (3, 4), (4, 7)]
    for score_val, expected_days in cases:
        scores = {k: score_val for k in ["correctness", "efficiency", "code_quality", "pattern_recognition", "explain_back"]}
        result = ps.log_attempt("algo", f"nc_0{score_val:02d}0", scores=scores)
        expected = (date.today() + timedelta(days=expected_days)).isoformat()
        assert result["review_scheduled"] == expected, f"score {score_val} expected {expected_days} days"


def test_log_attempt_replaces_existing_review_entry(data_dir):
    ps = get_server(data_dir)
    scores_low = {"correctness": 2, "efficiency": 2, "code_quality": 2, "pattern_recognition": 2, "explain_back": 2}
    ps.log_attempt("algo", "nc_015", scores=scores_low)
    scores_high = {"correctness": 4, "efficiency": 4, "code_quality": 4, "pattern_recognition": 4, "explain_back": 4}
    ps.log_attempt("algo", "nc_015", scores=scores_high)
    rq = read_review_queue(data_dir)
    entries = [i for i in rq["items"] if i["item_id"] == "nc_015"]
    assert len(entries) == 1  # not duplicated
    expected = (date.today() + timedelta(days=7)).isoformat()
    assert entries[0]["scheduled_date"] == expected


def test_log_attempt_hints_and_timed_mock(data_dir):
    ps = get_server(data_dir)
    scores = {"correctness": 4, "efficiency": 4, "code_quality": 4, "pattern_recognition": 4, "explain_back": 4}
    ps.log_attempt("algo", "nc_015", scores=scores, hints_used=2, timed_mock=True, within_time_limit=True)
    data = read_attempts(data_dir)
    attempt = data["attempts"][0]
    assert attempt["hints_used"] == 2
    assert attempt["timed_mock"] is True
    assert attempt["within_time_limit"] is True


# ── get_due_reviews ────────────────────────────────────────────────────────

def test_get_due_reviews_empty_when_none_due(data_dir):
    ps = get_server(data_dir)
    assert ps.get_due_reviews() == []


def test_get_due_reviews_returns_due_items(data_dir):
    ps = get_server(data_dir)
    # Manually insert an overdue review item
    rq_path = data_dir / "review_queue.json"
    rq = {"items": [{"track": "algo", "item_id": "nc_010", "scheduled_date": "2026-01-01", "last_score": 2, "added_date": "2025-12-31"}]}
    rq_path.write_text(json.dumps(rq, indent=2))
    import importlib; import servers.progress_server as ps_mod; importlib.reload(ps_mod)
    ps = get_server(data_dir)
    result = ps.get_due_reviews()
    assert len(result) == 1
    assert result[0]["item_id"] == "nc_010"


def test_get_due_reviews_excludes_future_items(data_dir):
    ps = get_server(data_dir)
    future = (date.today() + timedelta(days=5)).isoformat()
    rq_path = data_dir / "review_queue.json"
    rq = {"items": [{"track": "algo", "item_id": "nc_010", "scheduled_date": future, "last_score": 3, "added_date": "2026-03-01"}]}
    rq_path.write_text(json.dumps(rq, indent=2))
    import importlib; import servers.progress_server as ps_mod; importlib.reload(ps_mod)
    ps = get_server(data_dir)
    assert ps.get_due_reviews() == []


# ── clear_review ───────────────────────────────────────────────────────────

def test_clear_review_removes_item(data_dir):
    ps = get_server(data_dir)
    scores = {"correctness": 2, "efficiency": 2, "code_quality": 2, "pattern_recognition": 2, "explain_back": 2}
    ps.log_attempt("algo", "nc_015", scores=scores)
    ps.clear_review("algo", "nc_015")
    rq = read_review_queue(data_dir)
    assert all(i["item_id"] != "nc_015" for i in rq["items"])


def test_clear_review_not_present_is_safe(data_dir):
    ps = get_server(data_dir)
    result = ps.clear_review("algo", "nc_999")
    assert result["ok"] == "true"


# ── get_weak_areas ─────────────────────────────────────────────────────────

def test_get_weak_areas_empty_before_attempts(data_dir):
    ps = get_server(data_dir)
    result = ps.get_weak_areas()
    assert result["weak"] == []
    assert result["moderate"] == []


def test_get_weak_areas_flags_low_scores(data_dir):
    ps = get_server(data_dir)
    # Log two low-scoring attempts on nc_015 (has sliding_window tag)
    low_scores = {"correctness": 2, "efficiency": 2, "code_quality": 2, "pattern_recognition": 2, "explain_back": 2}
    ps.log_attempt("algo", "nc_015", scores=low_scores)
    ps.log_attempt("algo", "nc_015", scores=low_scores)
    result = ps.get_weak_areas()
    weak_tags = [w["tag"] for w in result["weak"]]
    assert "sliding_window" in weak_tags or "arrays" in weak_tags


def test_get_weak_areas_sorted_worst_first(data_dir):
    ps = get_server(data_dir)
    # Two attempts: one low, one very low
    ps.log_attempt("algo", "nc_015", scores={"correctness": 1, "efficiency": 1, "code_quality": 1, "pattern_recognition": 1, "explain_back": 1})
    ps.log_attempt("algo", "nc_015", scores={"correctness": 2, "efficiency": 2, "code_quality": 2, "pattern_recognition": 2, "explain_back": 2})
    result = ps.get_weak_areas()
    if len(result["weak"]) >= 2:
        scores = [w["avg_score"] for w in result["weak"]]
        assert scores == sorted(scores)


# ── get_last_completed ─────────────────────────────────────────────────────

def test_get_last_completed_returns_none_when_empty(data_dir):
    ps = get_server(data_dir)
    result = ps.get_last_completed("gof")
    assert result is None


def test_get_last_completed_returns_last_id(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("gof", "gof_001")
    ps.add_completed("gof", "gof_002")
    result = ps.get_last_completed("gof")
    assert result["id"] == "gof_002"


def test_get_last_completed_algo_returns_last(data_dir):
    ps = get_server(data_dir)
    # Fixture has nc_001..nc_014 completed; nc_014 should be last
    result = ps.get_last_completed("algo")
    assert result["id"] == "nc_014"


# ── get_evening_drill ──────────────────────────────────────────────────────

def test_evening_drill_skips_when_session_active(data_dir):
    ps = get_server(data_dir)
    ps.set_in_progress("algo", "nc_015")
    result = ps.get_evening_drill()
    assert result.get("session_active") is True


def test_evening_drill_uses_last_completed_when_available(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("gof", "gof_001")
    ps.add_completed("gof", "gof_002")
    # No session in progress — should return one of the completed patterns
    result = ps.get_evening_drill()
    assert result["session_active"] is False
    assert result["is_review"] is True
    assert result["id"] in ("gof_001", "gof_002")


def test_evening_drill_avoids_last_drill_id(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("gof", "gof_001")
    ps.add_completed("gof", "gof_002")
    # Simulate last_drill_id = gof_002 — should return gof_001
    import json
    progress_file = data_dir / "progress.json"
    data = json.loads(progress_file.read_text())
    data["last_drill_id"] = "gof_002"
    progress_file.write_text(json.dumps(data))
    result = ps.get_evening_drill()
    assert result["id"] == "gof_001"


def test_evening_drill_no_completed_returns_no_completed_flag(data_dir):
    ps = get_server(data_dir)
    # Nothing completed — drill should not show unstarted patterns
    result = ps.get_evening_drill()
    assert result["session_active"] is False
    assert result.get("no_completed") is True
    assert "id" not in result


# ── get_category_summary ───────────────────────────────────────────────────

def test_category_summary_returns_false_when_incomplete(data_dir):
    ps = get_server(data_dir)
    # nc_015 not yet completed — category not done
    result = ps.get_category_summary("algo", "nc_015")
    assert result["completed"] is False


def test_category_summary_returns_summary_when_complete(data_dir):
    ps = get_server(data_dir)
    # nc_015 is the only algo file in the fixture's data dir,
    # so completing it makes that category fully done
    ps.add_completed("algo", "nc_015")
    result = ps.get_category_summary("algo", "nc_015")
    assert result["completed"] is True
    assert result["category"] == "Sliding Window"
    assert result["problem_count"] >= 1
    assert "key_patterns" in result
    assert any(p["tag"] in ("sliding_window", "arrays") for p in result["key_patterns"])
    assert "techniques" in result
    assert "pattern_cue" in result
    # Sliding Window has category insights defined
    assert isinstance(result["techniques"], list)
    assert isinstance(result["pattern_cue"], str)


def test_category_summary_non_algo_returns_false(data_dir):
    ps = get_server(data_dir)
    result = ps.get_category_summary("sql", "sql_001")
    assert result["completed"] is False


# ── get_quiz_problem ───────────────────────────────────────────────────────

def test_get_quiz_problem_returns_completed_problem(data_dir):
    ps = get_server(data_dir)
    # nc_015.json exists in fixture; add it to completed so it's eligible
    ps.add_completed("algo", "nc_015")
    result = ps.get_quiz_problem()
    assert "error" not in result
    assert result["id"] == "nc_015"
    assert "title" in result
    assert "description" in result
    assert "answer" in result
    assert "category" in result["answer"]
    assert "pattern_tags" in result["answer"]


def test_get_quiz_problem_saves_last_quiz_id(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    ps.get_quiz_problem()
    data = read_progress(data_dir)
    assert data.get("last_quiz_id") == "nc_015"


def test_get_quiz_problem_no_completed_returns_error(data_dir):
    ps = get_server(data_dir)
    # Clear completed list
    import json
    prog = read_progress(data_dir)
    prog["completed_problem_ids"] = []
    (data_dir / "progress.json").write_text(json.dumps(prog, indent=2))
    import importlib; import servers.progress_server as ps_mod; importlib.reload(ps_mod)
    ps = get_server(data_dir)
    result = ps.get_quiz_problem()
    assert "error" in result


def test_get_quiz_problem_avoids_last_quiz_id(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    # Set last_quiz_id to nc_015 — with only one eligible problem, pool falls back gracefully
    import json
    prog = read_progress(data_dir)
    prog["last_quiz_id"] = "nc_015"
    (data_dir / "progress.json").write_text(json.dumps(prog, indent=2))
    import importlib; import servers.progress_server as ps_mod; importlib.reload(ps_mod)
    ps = get_server(data_dir)
    # Only nc_015 available and it's excluded — should return error (pool empty)
    result = ps.get_quiz_problem()
    assert "error" in result


# ── weekly goal tracking ────────────────────────────────────────────────────

def test_add_completed_increments_week_completions(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    data = read_progress(data_dir)
    assert data["week_completions"]["algo"] == 1


def test_add_completed_weekly_idempotent(data_dir):
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    ps.add_completed("algo", "nc_015")  # already done — should not double-count
    data = read_progress(data_dir)
    assert data["week_completions"]["algo"] == 1


def test_add_completed_resets_week_on_new_monday(data_dir):
    ps = get_server(data_dir)
    # Simulate a stale week by injecting old week_start and previous counts
    prog = read_progress(data_dir)
    prog["week_start"] = "2026-01-05"  # old Monday
    prog["week_completions"] = {"algo": 4, "sql": 0, "gof": 0, "aiml": 0}
    (data_dir / "progress.json").write_text(json.dumps(prog, indent=2))
    import importlib; import servers.progress_server as ps_mod; importlib.reload(ps_mod)
    ps = get_server(data_dir)
    ps.add_completed("algo", "nc_015")
    after = read_progress(data_dir)
    # Old count should be reset; new count should be 1
    assert after["week_completions"]["algo"] == 1
    # week_start should be updated to current Monday
    today = date.today()
    expected_monday = (today - timedelta(days=today.weekday())).isoformat()
    assert after["week_start"] == expected_monday


def test_add_completed_only_tracks_weekly_goal_tracks(data_dir):
    ps = get_server(data_dir)
    # behavioral and system_design are not in WEEKLY_GOALS — no week_completions key
    ps.add_completed("behavioral", "bq_001")
    data = read_progress(data_dir)
    assert "behavioral" not in data.get("week_completions", {})


# ── get_greeting_card ───────────────────────────────────────────────────────

def test_get_greeting_card_includes_week_progress(data_dir):
    ps = get_server(data_dir)
    result = ps.get_greeting_card()
    assert "week_completions" in result
    assert "week_goals" in result
    assert result["week_goals"]["algo"] == 20
    assert result["week_completions"]["algo"] == 0


def test_get_greeting_card_includes_pattern_context(data_dir):
    ps = get_server(data_dir)
    result = ps.get_greeting_card()
    # nc_015 is first algo item; its fixture has pattern_tags = ["sliding_window", "arrays"]
    first_algo = result["next"]["algo"][0]
    assert first_algo["id"] == "nc_015"
    assert "pattern_context" in first_algo
    assert "tags" in first_algo["pattern_context"]
    assert "sliding_window" in first_algo["pattern_context"]["tags"]


def test_get_greeting_card_pattern_context_counts_done(data_dir):
    ps = get_server(data_dir)
    # Log an attempt for nc_015 so problems_done_with_tag becomes 1
    scores = {"correctness": 4, "efficiency": 4, "code_quality": 4, "pattern_recognition": 4, "explain_back": 4}
    ps.log_attempt("algo", "nc_015", scores=scores)
    result = ps.get_greeting_card()
    first_algo = result["next"]["algo"][0]
    assert first_algo["pattern_context"]["problems_done_with_tag"] >= 1


# ── confidence decay ────────────────────────────────────────────────────────

def test_get_weak_areas_returns_decayed_key(data_dir):
    ps = get_server(data_dir)
    result = ps.get_weak_areas()
    assert "decayed" in result


def test_get_weak_areas_decayed_tag_appears_after_14_days(data_dir):
    ps = get_server(data_dir)
    # Inject a weak_areas.json entry with decayed=True manually
    old_date = (date.today() - timedelta(days=15)).isoformat()
    wa = {
        "schema_version": "1.0",
        "last_computed": old_date,
        "by_pattern_tag": {
            "two_pointers": {
                "avg_score": 4.2,
                "attempt_count": 3,
                "below_threshold": False,
                "last_attempt_date": old_date,
                "decayed": True,
            }
        }
    }
    (data_dir / "weak_areas.json").write_text(json.dumps(wa, indent=2))
    import importlib; import servers.progress_server as ps_mod; importlib.reload(ps_mod)
    ps = get_server(data_dir)
    result = ps.get_weak_areas()
    assert len(result["decayed"]) == 1
    assert result["decayed"][0]["tag"] == "two_pointers"
