"""
MCP server for interview prep progress management.
Handles all reads/writes to progress.json — the LLM never calculates queue order.
"""
import json
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import ATTEMPTS_FILE, DATA_DIR, NOTES_FILE, PROGRESS_FILE, REVIEW_FILE, TIMER_FILE, WEAK_AREAS_FILE

mcp = FastMCP("interview-prep-progress")

# ── Sequences (defines queue order per track) ──────────────────────────────

ALGO_SEQ = [f"nc_{i:03d}" for i in range(1, 150)]
SQL_SEQ  = [f"sql_{i:03d}" for i in range(1, 66)]
GOF_SEQ  = [
    *[f"gof_{i:03d}" for i in range(1, 24)],
    # SOLID principles (after all GoF patterns)
    "solid_001", "solid_002", "solid_003", "solid_004", "solid_005",
]
AIML_SEQ = [
    # Math phase
    "ml_m01","ml_m02","ml_m03","ml_m04","ml_m05",
    "ml_m06","ml_m07","ml_m08","ml_m09","ml_m10",
    # Core ML
    "ml_c01","ml_c02","ml_c03","ml_c04","ml_c05","ml_c06","ml_c07","ml_c08",
    # Deep Learning
    "ml_d01","ml_d02","ml_d03","ml_d04","ml_d05",
    # Frontier AI
    "ml_f01","ml_f02","ml_f03","ml_f04","ml_f05",
    # ML System Design
    "ml_sd01","ml_sd02","ml_sd03","ml_sd04","ml_sd05","ml_sd06","ml_sd07","ml_sd08",
]
BEHAVIORAL_SEQ = [f"bq_{i:03d}" for i in range(1, 31)]
NC_CORE_SEQ = [
    # Dynamic programming concepts + implementations
    "nc_core_dp01", "nc_core_dp02",
    "nc_core_dp_impl01", "nc_core_dp_impl02", "nc_core_dp_impl03",
    "nc_core_dp_impl04", "nc_core_dp_impl05", "nc_core_dp_impl06",
    "nc_core_dp_impl07", "nc_core_dp_impl08", "nc_core_dp_impl09", "nc_core_dp_impl10",
    # Data structures
    "nc_core_ds01", "nc_core_ds02", "nc_core_ds03", "nc_core_ds04", "nc_core_ds05",
    "nc_core_ds06", "nc_core_ds07", "nc_core_ds08", "nc_core_ds09",
    # Graphs
    "nc_core_g01", "nc_core_g02", "nc_core_g03",
    "nc_core_g04", "nc_core_g05", "nc_core_g06",
    # ML
    "nc_core_ml01", "nc_core_ml02", "nc_core_ml03",
    # Strings/search
    "nc_core_s01", "nc_core_s02", "nc_core_s03",
]
DS_SEQ = [
    "ds_a01", "ds_h01", "ds_tp01", "ds_sw01", "ds_st01",
    "ds_bs01", "ds_ll01", "ds_bt01", "ds_hp01", "ds_tr01",
    "ds_g01", "ds_dp01", "ds_dp02", "ds_bk01", "ds_bm01",
    "ds_gr01", "ds_iv01", "ds_mg01", "ds_ag01",
]
SYSTEM_DESIGN_SEQ = [
    # Concepts
    *[f"sd_c{i:02d}" for i in range(1, 16)],
    # Object design
    *[f"sd_o{i:02d}" for i in range(1, 7)],
    # Scalability
    *[f"sd_s{i:02d}" for i in range(1, 5)],
    # Deep dives
    *[f"sd_d{i:02d}" for i in range(1, 9)],
    # Live mocks
    *[f"sd_l{i:02d}" for i in range(1, 9)],
]

SEQUENCES: dict[str, list[str]] = {
    "algo":          ALGO_SEQ,
    "sql":           SQL_SEQ,
    "gof":           GOF_SEQ,
    "aiml":          AIML_SEQ,
    "behavioral":    BEHAVIORAL_SEQ,
    "system_design": SYSTEM_DESIGN_SEQ,
    "nc_core":       NC_CORE_SEQ,
    "ds":            DS_SEQ,
}

# ── Track → progress.json field mapping ───────────────────────────────────

TRACK_FIELDS: dict[str, dict[str, str | None]] = {
    "algo": {
        "completed": "completed_problem_ids",
        "postponed": "postponed_problem_ids",
        "stat":      "total_problems_solved",
    },
    "sql": {
        "completed": "completed_sql_ids",
        "postponed": "postponed_sql_ids",
        "stat":      "total_sql_solved",
    },
    "gof": {
        "completed": "completed_pattern_ids",
        "postponed": "postponed_pattern_ids",
        "stat":      "total_pattern_sessions",
    },
    "aiml": {
        "completed": "completed_concept_ids",
        "postponed": "postponed_concept_ids",
        "stat":      "total_aiml_sessions",
    },
    "behavioral": {
        "completed": "completed_behavioral_ids",
        "postponed": "postponed_behavioral_ids",
        "stat":      "total_behavioral_sessions",
    },
    "system_design": {
        "completed": "completed_design_ids",
        "postponed": "postponed_design_ids",
        "stat":      "total_design_mocks",
    },
    "nc_core": {
        "completed": "completed_core_ids",
        "postponed": "postponed_core_ids",
        "stat":      None,
    },
    "ds": {
        "completed": "completed_ds_ids",
        "postponed": "postponed_ds_ids",
        "stat":      None,
    },
    # Language quiz — no completion tracking (random pick, no queue)
    "lang": {
        "completed": None,
        "postponed": None,
        "stat":      None,
    },
}

POSTPONE_LIMIT = 3

def _lang_quiz_active_languages() -> set[str]:
    """TypeScript-only until June 2026, then Python and C# added automatically."""
    today = datetime.now(timezone.utc).date()
    langs = {"TypeScript"}
    if today >= date(2026, 6, 1):
        langs |= {"Python", "C#"}
    return langs

# Weekly goal targets (algo, sql, gof, aiml only)
WEEKLY_GOALS: dict[str, int] = {"algo": 15, "sql": 5, "gof": 3, "ds": 3, "nc_core": 4, "system_design": 4, "behavioral": 5, "aiml": 4}

# ── Helpers ────────────────────────────────────────────────────────────────

def _load() -> dict[str, Any]:
    with open(PROGRESS_FILE) as f:
        return json.load(f)

def _save(data: dict[str, Any]) -> None:
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # trailing newline

def _today_pst() -> str:
    """Return today's date in PST/PDT as YYYY-MM-DD."""
    now_utc = datetime.now(timezone.utc)
    # March–October = UTC-7 (PDT), November–February = UTC-8 (PST)
    month = now_utc.month
    offset_hours = -7 if 3 <= month <= 10 else -8
    local = now_utc + timedelta(hours=offset_hours)
    return local.strftime("%Y-%m-%d")


def _week_start_pst() -> str:
    """Return the Monday of the current PST week as YYYY-MM-DD."""
    from datetime import date
    today = datetime.strptime(_today_pst(), "%Y-%m-%d").date()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()

def _update_streak(data: dict[str, Any], today: str) -> None:
    last = data.get("last_active_date")
    if last == today:
        return  # already updated today
    if last:
        last_dt = datetime.strptime(last, "%Y-%m-%d").date()
        today_dt = datetime.strptime(today, "%Y-%m-%d").date()
        delta = (today_dt - last_dt).days
        if delta == 1:
            data["streak_days"] = data.get("streak_days", 0) + 1
        elif delta > 1:
            data["streak_days"] = 1
    else:
        data["streak_days"] = 1
    data["last_active_date"] = today

def _validate_track(track: str) -> None:
    if track not in TRACK_FIELDS:
        raise ValueError(f"Unknown track '{track}'. Valid: {list(TRACK_FIELDS)}")

# ── Secondary file helpers ──────────────────────────────────────────────────

def _load_file(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)

def _save_file(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def _this_monday(today: str) -> str:
    """Return the most recent Monday as YYYY-MM-DD."""
    d = datetime.strptime(today, "%Y-%m-%d").date()
    return (d - timedelta(days=d.weekday())).isoformat()

def _check_week_reset(data: dict[str, Any], today: str) -> bool:
    """Reset week_completions if we've crossed into a new Monday. Returns True if reset."""
    monday = _this_monday(today)
    if data.get("week_start") != monday:
        data["week_start"] = monday
        data["week_completions"] = {k: 0 for k in WEEKLY_GOALS}
        return True
    return False

def _review_delay_days(score: float) -> int:
    """Days until next review based on composite score. Score 5 = no review."""
    s = round(score)
    return {1: 1, 2: 2, 3: 4, 4: 7}.get(s, 0)

def _recompute_weak_areas() -> None:
    """Full recompute of weak_areas.json from all attempts. Called after log_attempt."""
    attempts_data = _load_file(ATTEMPTS_FILE, {"attempts": []})
    tag_scores: dict[str, list[float]] = {}
    tag_last_date: dict[str, str] = {}
    for attempt in attempts_data["attempts"]:
        tags = attempt.get("pattern_tags", [])
        score = attempt.get("composite_score", 0.0)
        ts_date = attempt.get("timestamp", "")[:10]  # YYYY-MM-DD prefix
        for tag in tags:
            tag_scores.setdefault(tag, []).append(score)
            if ts_date > tag_last_date.get(tag, ""):
                tag_last_date[tag] = ts_date
    today = _today_pst()
    by_tag: dict[str, Any] = {}
    for tag, scores in tag_scores.items():
        avg = round(sum(scores) / len(scores), 2)
        last_date = tag_last_date.get(tag, today)
        try:
            days_since = (
                datetime.strptime(today, "%Y-%m-%d").date() -
                datetime.strptime(last_date, "%Y-%m-%d").date()
            ).days
        except Exception:
            days_since = 0
        by_tag[tag] = {
            "avg_score": avg,
            "attempt_count": len(scores),
            "below_threshold": avg < 3.0,
            "last_attempt_date": last_date,
            "decayed": days_since >= 14 and avg >= 3.0,  # good score but not practiced lately
        }
    _save_file(WEAK_AREAS_FILE, {
        "schema_version": "1.0",
        "last_computed": today,
        "by_pattern_tag": by_tag,
    })

# ── Category insights (static pedagogical notes per category) ──────────────

CATEGORY_INSIGHTS: dict[str, dict[str, Any]] = {
    "Arrays": {
        "techniques": [
            "Frequency maps — count with a hash map before you iterate; turns O(n²) lookups into O(1)",
            "Setting invariants — define exactly what must be true at every loop step (e.g. window is valid, left ≤ right); the invariant tells you when to expand or contract",
            "Identify what you need first — lookup? → hash map. Contiguous subarray? → sliding window. Sorted input? → two pointers or binary search. Range queries? → prefix sums",
            "Prefix sums — precompute cumulative sums once for O(1) subarray sum queries",
            "In-place swaps — most space-O(1) problems reduce to swapping; draw the before/after first",
        ],
        "pattern_cue": "Unsorted + pair target → hash map or two pointers. Subarray sum/max/min → sliding window. Sorted → binary search or two pointers. Range query → prefix sum.",
    },
    "Two Pointers": {
        "techniques": [
            "Invariant first — decide what the left/right pointers represent and what condition moves each",
            "Sorted input is usually required — if unsorted, sort first or use a hash map instead",
            "Avoid duplicates by skipping equal adjacent values after processing",
            "Fast/slow pointer variant — detect cycles or find midpoints in O(1) space",
        ],
        "pattern_cue": "Pair/triplet sum in sorted array → two pointers. Cycle detection → fast/slow. Remove duplicates in-place → left pointer as write head.",
    },
    "Sliding Window": {
        "techniques": [
            "Expand right unconditionally, contract left only when the window becomes invalid",
            "Track window state with a counter or hash map — avoid recomputing from scratch each step",
            "Fixed vs variable size — fixed: move both pointers together. Variable: only contract when invalid",
            "The answer is usually updated right before or right after contraction",
        ],
        "pattern_cue": "Longest/shortest subarray with constraint → variable sliding window. Subarray of size k → fixed window. If constraint is on distinct elements → hash map + window.",
    },
    "Stack": {
        "techniques": [
            "Monotonic stack — maintain an increasing or decreasing stack to find next greater/smaller in O(n)",
            "Match open/close pairs by pushing opens and popping on close — valid if stack empty at end",
            "Think backwards — sometimes it's easier to process right-to-left with a stack",
            "Stack simulates recursion — any recursive DFS can be rewritten with an explicit stack",
        ],
        "pattern_cue": "Next greater/smaller element → monotonic stack. Balanced brackets → push/pop. Expression evaluation → two stacks (values + operators).",
    },
    "Binary Search": {
        "techniques": [
            "Search space, not just arrays — binary search works on any monotonic function, not just sorted lists",
            "Template: lo=0, hi=n-1, mid=lo+(hi-lo)//2. Move lo=mid+1 or hi=mid-1 to avoid infinite loop",
            "Off-by-one is the main bug — trace through a 2-element array to verify your boundary conditions",
            "Bisect left vs right — left finds first position where condition is true, right finds last",
        ],
        "pattern_cue": "Sorted array + O(log n) → binary search. 'Minimum maximum' or 'maximum minimum' → binary search on answer. Rotated sorted array → determine which half is sorted first.",
    },
    "Linked List": {
        "techniques": [
            "Dummy head — add a sentinel node before head to avoid edge cases on insertions/deletions at head",
            "Fast/slow pointers — cycle detection, midpoint, k-th from end all reduce to this pattern",
            "Draw the pointer reassignment — reversal bugs are almost always from reassigning in the wrong order; draw before writing code",
            "Two-pass trick — if you need length first, one pass to count, one to act",
        ],
        "pattern_cue": "Cycle → fast/slow. Reverse → prev/curr/next triple. Find middle → fast/slow stop when fast hits null. Merge two lists → dummy head + compare heads.",
    },
    "Trees": {
        "techniques": [
            "Recursion template — base case (null → return 0/null/False), recurse left, recurse right, combine",
            "Return type determines approach — if you need to bubble up two values, return a tuple or dataclass",
            "Pre/in/post order — pre=process node before children (top-down). In=sorted for BST. Post=aggregate children first (bottom-up)",
            "BFS for level-order — use a deque; process all nodes at depth d before depth d+1",
            "Path problems — carry a running value down via parameters, not return values",
        ],
        "pattern_cue": "Path sum/max → DFS with running total. Level-by-level → BFS. Validate BST → pass min/max bounds down. LCA → post-order: if both subtrees return non-null, current node is LCA.",
    },
    "Heap / Priority Queue": {
        "techniques": [
            "Min-heap by default in Python (heapq) — for max-heap, negate values",
            "K largest/smallest — maintain a heap of size k; push and pop to keep only k elements",
            "Two heaps trick — one max-heap for lower half, one min-heap for upper half (median maintenance)",
            "Lazy deletion — mark items as deleted instead of removing; skip them when popping",
        ],
        "pattern_cue": "Top-k elements → heap of size k. Merge k sorted lists → min-heap of (val, list_idx). Median of stream → two heaps. Dijkstra → min-heap of (distance, node).",
    },
    "Backtracking": {
        "techniques": [
            "Template: choose → explore → unchoose. The unchoose step is what makes it backtracking, not DFS",
            "Pruning is the performance lever — add constraints early to cut branches before recursing",
            "Avoid duplicates by sorting first and skipping equal siblings at the same tree level",
            "State is usually a mutable list passed by reference — append before recurse, pop after",
        ],
        "pattern_cue": "All subsets/permutations/combinations → backtracking. N-Queens, Sudoku → backtracking with constraint check. If only the count matters (not the actual combinations) → DP is faster.",
    },
    "Graphs": {
        "techniques": [
            "Visited set is mandatory — always track visited nodes to prevent infinite loops",
            "BFS = shortest path in unweighted graphs. DFS = connectivity, cycle detection, topological sort",
            "Build adjacency list from edge list before searching — don't search the raw edge list",
            "Topological sort — Kahn's algorithm (BFS + in-degree) for cycle detection; DFS post-order for ordering",
            "Union-Find — fastest for dynamic connectivity queries; path compression + union by rank = near O(1)",
        ],
        "pattern_cue": "Shortest path (unweighted) → BFS. Connected components → DFS or Union-Find. Has cycle → DFS with recursion stack or Union-Find. Dependencies/ordering → topological sort.",
    },
    "Dynamic Programming": {
        "techniques": [
            "State definition is the hardest part — ask 'what info do I need at this step to make the optimal choice?'",
            "Draw the recurrence before writing code — dp[i] = f(dp[i-1], dp[i-2], ...)",
            "Top-down (memoization) is easier to write; bottom-up (tabulation) is easier to optimize space",
            "Space optimization — if dp[i] only depends on dp[i-1], you only need two variables",
            "2D DP — rows are usually one sequence, columns the other; fill row by row",
        ],
        "pattern_cue": "Optimal substructure + overlapping subproblems → DP. Choices at each step → decision DP. Two sequences to align/match → 2D DP. Partitioning → subset-sum style DP.",
    },
    "Greedy": {
        "techniques": [
            "Prove correctness by exchange argument — show that swapping any greedy choice for another never improves the solution",
            "Sort first — most greedy problems become obvious after sorting by the right key",
            "Interval problems — sort by end time for minimum coverage; sort by start time for merging",
            "Greedy fails when local optimum ≠ global optimum — if you can construct a counterexample, use DP",
        ],
        "pattern_cue": "Activity selection / interval scheduling → sort by end, greedily pick. Jump game → track max reachable index. Huffman / minimum cost → priority queue greedy.",
    },
}

# ── Category map (lazy, built once from algo files) ────────────────────────

_ALGO_CATEGORY_MAP: dict[str, list[str]] | None = None

def _get_algo_category_map() -> dict[str, list[str]]:
    global _ALGO_CATEGORY_MAP
    if _ALGO_CATEGORY_MAP is not None:
        return _ALGO_CATEGORY_MAP
    cat_map: dict[str, list[str]] = {}
    for pid in ALGO_SEQ:
        try:
            prob = json.load(open(DATA_DIR / "algo" / f"{pid}.json"))
            cat = prob.get("category", "Unknown")
            cat_map.setdefault(cat, []).append(pid)
        except Exception:
            pass
    _ALGO_CATEGORY_MAP = cat_map
    return cat_map

# ── MCP Tools ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_progress() -> dict[str, Any]:
    """
    Return current progress summary — streak, stats, in_progress item,
    and completed counts for every track.
    Does NOT return full ID lists (use get_next_items for queue).
    """
    data = _load()
    completed_counts = {
        "algo":          len(data.get("completed_problem_ids", [])),
        "sql":           len(data.get("completed_sql_ids", [])),
        "gof":           len(data.get("completed_pattern_ids", [])),
        "aiml":          len(data.get("completed_concept_ids", [])),
        "behavioral":    len(data.get("completed_behavioral_ids", [])),
        "system_design": len(data.get("completed_design_ids", [])),
        "nc_core":       len(data.get("completed_core_ids", [])),
        "ds":            len(data.get("completed_ds_ids", [])),
    }
    return {
        "streak_days":       data.get("streak_days", 0),
        "last_active_date":  data.get("last_active_date"),
        "start_date":        data.get("start_date"),
        "in_progress":       data.get("in_progress"),
        "stats":             data.get("stats", {}),
        "completed_counts":  completed_counts,
    }


def _get_title(track: str, id_: str) -> str:
    """Read just the title for one item. Falls back to id on any error."""
    try:
        if track == "algo":
            d = json.load(open(DATA_DIR / "algo" / f"{id_}.json"))
            return d.get("title", id_)
        elif track == "sql":
            d = json.load(open(DATA_DIR / "sql" / f"{id_}.json"))
            return d.get("title", id_)
        elif track == "gof":
            d = json.load(open(DATA_DIR / "gof" / f"{id_}.json"))
            return d.get("name", id_)
        elif track == "aiml":
            d = json.load(open(DATA_DIR / "aiml" / f"{id_}.json"))
            return d.get("title", id_)
        elif track == "behavioral":
            data = json.load(open(DATA_DIR / "behavioral.json"))
            for comp in data["behavioral"]["competencies"].values():
                for q in comp["questions"]:
                    if q["id"] == id_:
                        return q.get("question", id_)[:60] + "…"
        elif track == "system_design":
            data = json.load(open(DATA_DIR / "system_design.json"))
            for level in data["system_design"]["levels"].values():
                for item in level.get("problems", level.get("topics", [])):
                    if item["id"] == id_:
                        return item.get("title", id_)
        elif track == "nc_core":
            d = json.load(open(DATA_DIR / "core" / f"{id_}.json"))
            return d.get("title", id_)
        elif track == "ds":
            data = json.load(open(DATA_DIR / "data_structures.json"))
            for c in data["ds_concepts"]:
                if c["id"] == id_:
                    return c.get("title", id_)
    except Exception:
        pass
    return id_


@mcp.tool()
def get_greeting_card() -> dict[str, Any]:
    """
    Return everything needed to render the greeting card in a single call:
    - progress (streak, stats, completed_counts)
    - next items for algo (3), sql (2), gof (1), aiml (1)
    - title for each item

    Use this instead of calling get_progress + get_next_items + get_item_titles separately.
    """
    data = _load()

    # Completed counts
    completed_counts = {
        "algo":          len(data.get("completed_problem_ids", [])),
        "sql":           len(data.get("completed_sql_ids", [])),
        "gof":           len(data.get("completed_pattern_ids", [])),
        "aiml":          len(data.get("completed_concept_ids", [])),
        "behavioral":    len(data.get("completed_behavioral_ids", [])),
        "system_design": len(data.get("completed_design_ids", [])),
        "nc_core":       len(data.get("completed_core_ids", [])),
        "ds":            len(data.get("completed_ds_ids", [])),
    }

    # Next items per track
    def _next(track: str, n: int) -> list[dict[str, Any]]:
        fields = TRACK_FIELDS[track]
        completed = set(data.get(fields["completed"], []))
        postponed = data.get(fields["postponed"], [])
        sequence = SEQUENCES[track]
        result: list[dict[str, Any]] = []
        for pid in postponed:
            if len(result) >= n:
                break
            result.append({"id": pid, "postponed": True})
        assigned = {r["id"] for r in result}
        for item_id in sequence:
            if len(result) >= n:
                break
            if item_id not in completed and item_id not in assigned:
                result.append({"id": item_id, "postponed": False})
        return result

    tracks = {
        "algo":          _next("algo",          3),
        "sql":           _next("sql",           2),
        "gof":           _next("gof",           1),
        "ds":            _next("ds",            1),
        "nc_core":       _next("nc_core",       1),
        "system_design": _next("system_design", 1),
        "behavioral":    _next("behavioral",    1),
        "aiml":          _next("aiml",          1),
    }

    # Enrich with titles
    for track, items in tracks.items():
        for item in items:
            item["title"] = _get_title(track, item["id"])

    # Pattern context for first algo item (tag + how many problems done with that tag)
    if tracks["algo"]:
        first_algo = tracks["algo"][0]
        try:
            prob_data = json.load(open(DATA_DIR / "algo" / f"{first_algo['id']}.json"))
            first_algo_tags = prob_data.get("pattern_tags", prob_data.get("tags", []))
            if first_algo_tags:
                attempts_data = _load_file(ATTEMPTS_FILE, {"attempts": []})
                done_ids = {
                    a["item_id"] for a in attempts_data["attempts"]
                    if set(a.get("pattern_tags", [])) & set(first_algo_tags)
                }
                first_algo["pattern_context"] = {
                    "tags": first_algo_tags,
                    "problems_done_with_tag": len(done_ids),
                }
        except Exception:
            pass

    # Weekly progress
    today = _today_pst()
    week_reset = _check_week_reset(data, today)
    if week_reset:
        _save(data)
    week_completions = data.get("week_completions", {k: 0 for k in WEEKLY_GOALS})

    # Week number (1-based, from start_date)
    start_date_str = data.get("start_date")
    if start_date_str:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        today_dt = datetime.strptime(today, "%Y-%m-%d").date()
        week_number = (today_dt - start_dt).days // 7 + 1
    else:
        week_number = 1

    # Due reviews
    rq = _load_file(REVIEW_FILE, {"items": []})
    due_reviews = [
        {**item, "title": _get_title(item["track"], item["item_id"])}
        for item in rq["items"]
        if item.get("scheduled_date", "9999") <= today
    ]
    due_reviews.sort(key=lambda x: x.get("scheduled_date", ""))

    return {
        "streak_days":      data.get("streak_days", 0),
        "last_active_date": data.get("last_active_date"),
        "start_date":       data.get("start_date"),
        "week_number":      week_number,
        "in_progress":      data.get("in_progress"),
        "stats":            data.get("stats", {}),
        "completed_counts": completed_counts,
        "next": tracks,
        "due_reviews":      due_reviews,
        "week_completions": week_completions,
        "week_goals":       WEEKLY_GOALS,
        "week_start":       data.get("week_start", _this_monday(today)),
    }


@mcp.tool()
def log_attempt(
    track: str,
    id: str,
    scores: dict[str, int],
    solution: str = "",
    hints_used: int = 0,
    timed_mock: bool = False,
    within_time_limit: bool | None = None,
    is_quiz: bool = False,
) -> dict[str, Any]:
    """
    Record a completed attempt with scores, solution, and metadata.
    - Computes composite_score server-side (mean of all provided scores).
    - Schedules spaced repetition review based on score (1→1d, 2→2d, 3→4d, 4→7d, 5→none).
    - Updates weak_areas.json automatically.
    - Copies pattern_tags from the problem file (algo only) for weak area tracking.

    Call this AFTER add_completed, passing the scores from your evaluation.

    Args:
        track: track name
        id: item ID (e.g. "nc_015")
        scores: e.g. {"brute_force": 4, "pattern_recognition": 4, "correctness": 4, "efficiency": 3, "code_quality": 4, "explain_back": 4}
        solution: user's code as a string (optional but recommended)
        hints_used: number of hints requested (0–3)
        timed_mock: whether this was a timed mock attempt
        within_time_limit: user's self-reported answer (null if not timed)

    Returns: composite_score, attempt_id, review_scheduled date (or null if score 5)
    """
    _validate_track(track)
    attempts_data = _load_file(ATTEMPTS_FILE, {"schema_version": "1.0", "attempts": []})

    composite = round(sum(scores.values()) / len(scores), 2) if scores else 0.0
    ts = int(datetime.now(timezone.utc).timestamp())
    attempt_id = f"a_{id}_{ts}"

    # Copy pattern_tags from problem file (algo only) for weak area tracking
    pattern_tags: list[str] = []
    if track == "algo":
        try:
            prob = json.load(open(DATA_DIR / "algo" / f"{id}.json"))
            pattern_tags = prob.get("pattern_tags", prob.get("tags", []))
        except Exception:
            pass

    attempt: dict[str, Any] = {
        "id": attempt_id,
        "track": track,
        "item_id": id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scores": scores,
        "composite_score": composite,
        "hints_used": hints_used,
        "timed_mock": timed_mock,
        "within_time_limit": within_time_limit,
        "pattern_tags": pattern_tags,
        "is_quiz": is_quiz,
    }
    if solution:
        attempt["solution"] = solution

    # Track lang quiz completion (mark complete on answer, not on pick)
    if track == "lang":
        progress_data = _load()
        completed_list = progress_data.setdefault("completed_lang_quiz_ids", [])
        if id not in completed_list:
            completed_list.append(id)
        _save(progress_data)

    # Increment daily quiz counter (resets each day)
    if is_quiz:
        progress_data = _load()
        today = _today_pst()
        if progress_data.get("quiz_today_date") != today:
            progress_data["quiz_today_date"] = today
            progress_data["quiz_today_count"] = 0
        progress_data["quiz_today_count"] = progress_data.get("quiz_today_count", 0) + 1
        _save(progress_data)

    # Increment weekly quiz counter (resets each Monday) — counts pop quiz + lang quiz
    if is_quiz or track == "lang":
        progress_data = _load()
        week_start = _week_start_pst()
        if progress_data.get("quiz_week_start") != week_start:
            progress_data["quiz_week_start"] = week_start
            progress_data["quiz_week_count"] = 0
        progress_data["quiz_week_count"] = progress_data.get("quiz_week_count", 0) + 1
        _save(progress_data)

    attempts_data["attempts"].append(attempt)
    _save_file(ATTEMPTS_FILE, attempts_data)

    # Schedule spaced repetition review
    delay = _review_delay_days(composite)
    review_date: str | None = None
    rq = _load_file(REVIEW_FILE, {"items": []})
    # Always remove existing entry for this item (clears stale reviews from earlier attempts)
    rq["items"] = [i for i in rq["items"] if not (i["item_id"] == id and i["track"] == track)]
    if delay > 0:
        from datetime import date, timedelta as td
        review_date = (datetime.strptime(_today_pst(), "%Y-%m-%d").date() + td(days=delay)).isoformat()
        rq["items"].append({
            "track": track,
            "item_id": id,
            "scheduled_date": review_date,
            "last_score": round(composite),
            "added_date": _today_pst(),
        })
    _save_file(REVIEW_FILE, rq)

    # Recompute weak areas
    if pattern_tags:
        _recompute_weak_areas()

    return {
        "attempt_id": attempt_id,
        "composite_score": composite,
        "review_scheduled": review_date,
    }


@mcp.tool()
def get_due_reviews() -> list[dict[str, Any]]:
    """
    Return review items due today or overdue, enriched with titles.
    Sorted by date ascending (most overdue first).
    Returns empty list if nothing due.
    """
    rq = _load_file(REVIEW_FILE, {"items": []})
    today = _today_pst()
    due = [i for i in rq["items"] if i.get("scheduled_date", "9999") <= today]
    due.sort(key=lambda x: x.get("scheduled_date", ""))
    for item in due:
        item["title"] = _get_title(item["track"], item["item_id"])
    return due


@mcp.tool()
def clear_review(track: str, item_id: str) -> dict[str, Any]:
    """
    Remove an item from the review queue after it has been reviewed.
    Call after completing a review session for an item.
    """
    rq = _load_file(REVIEW_FILE, {"items": []})
    before = len(rq["items"])
    rq["items"] = [i for i in rq["items"] if not (i["item_id"] == item_id and i["track"] == track)]
    _save_file(REVIEW_FILE, rq)
    return {"ok": "true", "removed": before - len(rq["items"]) > 0}


@mcp.tool()
def add_to_review(track: str, item_id: str, days: int = 0) -> dict[str, Any]:
    """
    Manually add any completed item to the review queue.
    Use when Mayu asks to review something specific, re-add a recently cleared item,
    or schedule extra practice outside the normal spaced repetition cycle.

    Args:
        track:   track name (e.g. "algo")
        item_id: item ID (e.g. "nc_016")
        days:    days from today to schedule the review (0 = today, 1 = tomorrow, etc.)

    Returns: {"ok": true, "scheduled_date": "2026-04-03", "title": "..."}
    """
    _validate_track(track)
    today = _today_pst()
    scheduled = (datetime.strptime(today, "%Y-%m-%d").date() + timedelta(days=days)).isoformat()

    rq = _load_file(REVIEW_FILE, {"items": []})
    # Replace any existing entry for this item
    rq["items"] = [i for i in rq["items"] if not (i["item_id"] == item_id and i["track"] == track)]
    rq["items"].append({
        "track": track,
        "item_id": item_id,
        "scheduled_date": scheduled,
        "last_score": None,
        "added_date": today,
    })
    _save_file(REVIEW_FILE, rq)
    return {"ok": True, "scheduled_date": scheduled, "title": _get_title(track, item_id)}


@mcp.tool()
def get_weak_areas() -> dict[str, Any]:
    """
    Return weak area analysis computed from all attempts.
    Weak = avg_score < 3.0 with at least 2 attempts.
    Decayed = not practiced in 14+ days (even if score was previously good).
    Returns pre-sorted lists — no arithmetic needed by the agent.
    """
    data = _load_file(WEAK_AREAS_FILE, {"by_pattern_tag": {}})
    by_tag = data.get("by_pattern_tag", {})

    weak = sorted(
        [{"tag": k, **v} for k, v in by_tag.items() if v.get("below_threshold") and v.get("attempt_count", 0) >= 2],
        key=lambda x: x["avg_score"]
    )
    moderate = sorted(
        [{"tag": k, **v} for k, v in by_tag.items() if not v.get("below_threshold") and v.get("avg_score", 5) < 3.5 and v.get("attempt_count", 0) >= 2],
        key=lambda x: x["avg_score"]
    )
    decayed = sorted(
        [{"tag": k, **v} for k, v in by_tag.items()
         if v.get("decayed") and not v.get("below_threshold") and v.get("attempt_count", 0) >= 1],
        key=lambda x: x.get("last_attempt_date", "")
    )
    return {
        "last_computed": data.get("last_computed"),
        "weak": weak,
        "moderate": moderate,
        "decayed": decayed,
    }


@mcp.tool()
def get_category_summary(track: str, item_id: str) -> dict[str, Any]:
    """
    Check if the category containing item_id is now fully completed.
    Call this after add_completed for algo problems.

    Returns {"completed": False} if the category is not yet done.
    Returns a full summary when the category is just finished:
      - category name, problem count, all problem titles
      - key_patterns: pattern tags sorted by frequency across problems in the category

    Use the summary to generate a category completion notification and prompt for notes.
    """
    if track != "algo":
        return {"completed": False}

    data = _load()
    completed_set = set(data.get("completed_problem_ids", []))

    try:
        prob = json.load(open(DATA_DIR / "algo" / f"{item_id}.json"))
        category = prob.get("category")
    except Exception:
        return {"completed": False}

    if not category:
        return {"completed": False}

    cat_map = _get_algo_category_map()
    cat_problems = cat_map.get(category, [])

    if not cat_problems or not all(p in completed_set for p in cat_problems):
        return {"completed": False}

    # Category is fully complete — build summary
    problems = []
    tag_counts: dict[str, int] = {}
    for pid in cat_problems:
        try:
            p = json.load(open(DATA_DIR / "algo" / f"{pid}.json"))
            tags = p.get("pattern_tags", p.get("tags", []))
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            problems.append({"id": pid, "title": p.get("title", pid)})
        except Exception:
            problems.append({"id": pid, "title": pid})

    key_patterns = [
        {"tag": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])
    ]
    insights = CATEGORY_INSIGHTS.get(category, {})
    return {
        "completed": True,
        "category": category,
        "problem_count": len(cat_problems),
        "problems": problems,
        "key_patterns": key_patterns,
        "techniques": insights.get("techniques", []),
        "pattern_cue": insights.get("pattern_cue", ""),
    }


@mcp.tool()
def start_timer(minutes: int, label: str) -> dict[str, Any]:
    """
    Start a countdown timer for a timed mock session.
    Writes expiry time to timer_queue.json — check_timer() fires the ping.

    Args:
        minutes: countdown duration (Easy=15, Medium=25, Hard=40)
        label: description shown when timer expires (e.g. "⏱️ Time's up — [title]!")

    Returns: {"started": true, "expires_at": ISO timestamp, "minutes": N}
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    entry = {
        "expires_at": expires_at.isoformat(),
        "label": label,
        "minutes": minutes,
    }
    TIMER_FILE.write_text(json.dumps(entry, indent=2))
    return {"started": True, "expires_at": expires_at.isoformat(), "minutes": minutes}


@mcp.tool()
def stop_timer() -> dict[str, Any]:
    """
    Stop the active timed mock timer without firing the ping.
    Call this immediately after Mayu submits her optimal code (before follow-up Q&A),
    so the timer measures coding time only — not Q&A time.
    Returns: {"stopped": true} if a timer was active, {"stopped": false} if none.
    """
    if TIMER_FILE.exists():
        TIMER_FILE.unlink(missing_ok=True)
        return {"stopped": True}
    return {"stopped": False}


@mcp.tool()
def check_timer() -> dict[str, Any]:
    """
    Check if a countdown timer has expired. Called by the /check-timer cron every minute.
    If expired: returns the label so the agent can ping Mayu, then clears the timer.
    If not expired: returns {"expired": false} — agent must output nothing and stop.
    If no timer set: returns {"expired": false}.
    """
    if not TIMER_FILE.exists():
        return {"expired": False}

    try:
        entry = json.loads(TIMER_FILE.read_text())
    except Exception:
        return {"expired": False}

    expires_at = datetime.fromisoformat(entry["expires_at"])
    if datetime.now(timezone.utc) >= expires_at:
        TIMER_FILE.unlink(missing_ok=True)
        return {"expired": True, "label": entry.get("label", "⏱️ Time's up!")}

    remaining = int((expires_at - datetime.now(timezone.utc)).total_seconds())
    m, s = divmod(remaining, 60)
    return {"expired": False, "remaining": f"{m}m {s}s"}


@mcp.tool()
def save_note(track: str, category: str, user_note: str, coach_note: str = "") -> dict[str, Any]:
    """
    Save takeaway notes for a track category (e.g. track="algo", category="Two Pointers").
    Stores both Mayu's raw takeaways and the coach's elaboration/feedback.
    Appends to notes.json — call after giving feedback on the user's takeaways.
    Returns: {"saved": true, "track": track, "category": category}
    """
    # Normalize category to consistent key (e.g. "Two Pointers" and "two_pointers" → same entry)
    category = category.strip()

    if NOTES_FILE.exists():
        data = json.loads(NOTES_FILE.read_text())
    else:
        data = {}

    if track not in data:
        data[track] = {}
    # Case-insensitive match against existing keys to avoid duplicates
    existing_key = next((k for k in data[track] if k.lower() == category.lower()), None)
    if existing_key:
        category = existing_key
    if category not in data[track]:
        data[track][category] = []
    data[track][category].append({
        "user_note": user_note,
        "coach_note": coach_note,
        "date": datetime.now(timezone.utc).date().isoformat(),
    })

    NOTES_FILE.write_text(json.dumps(data, indent=2))
    return {"saved": True, "track": track, "category": category}


@mcp.tool()
def reset_last_lang_quiz() -> dict[str, Any]:
    """
    Remove the last lang quiz question from completed_lang_quiz_ids and clear last_lang_quiz_id.
    Use when Mayu wants to redo the last question without it counting as completed.
    Returns: {"reset": true, "removed_id": "ts_001"} or {"reset": false} if nothing to reset.
    """
    data = _load()
    last_id = data.get("last_lang_quiz_id")
    if not last_id:
        return {"reset": False}

    completed = data.get("completed_lang_quiz_ids", [])
    if last_id in completed:
        completed.remove(last_id)
    data["last_lang_quiz_id"] = None
    _save(data)
    return {"reset": True, "removed_id": last_id}


@mcp.tool()
def save_behavioral_response(
    question_id: str,
    response: str,
    score: float,
    improvements: str = "",
) -> dict[str, Any]:
    """
    Save Mayu's behavioral response for a question. Keeps only the best response per question
    (highest composite score). Also stores suggested improvements.

    Args:
        question_id: e.g. "bq_001"
        response: Mayu's answer verbatim
        score: composite score (1.0–5.0)
        improvements: coach's bullet-point suggestions for improvement

    Returns: {"saved": true, "is_best": true/false, "previous_best": score or null}
    """
    bfile = DATA_DIR / "behavioral_responses.json"
    data = json.loads(bfile.read_text()) if bfile.exists() else {}

    existing = data.get(question_id)
    previous_best = existing["score"] if existing else None
    is_best = previous_best is None or score >= previous_best

    if is_best:
        data[question_id] = {
            "response": response,
            "score": score,
            "improvements": improvements,
            "date": _today_pst(),
        }
        bfile.write_text(json.dumps(data, indent=2))

    return {"saved": True, "is_best": is_best, "previous_best": previous_best}


@mcp.tool()
def get_behavioral_best(question_id: str) -> dict[str, Any]:
    """
    Retrieve the best saved response for a behavioral question.
    Returns: {"found": true, "response": "...", "score": N, "improvements": "...", "date": "..."}
    or {"found": false} if no response saved yet.
    """
    bfile = DATA_DIR / "behavioral_responses.json"
    if not bfile.exists():
        return {"found": False}
    data = json.loads(bfile.read_text())
    entry = data.get(question_id)
    if not entry:
        return {"found": False}
    return {"found": True, **entry}


@mcp.tool()
def get_notes(track: str, category: str) -> dict[str, Any]:
    """
    Retrieve saved takeaway notes for a track category (e.g. track="algo", category="Two Pointers").
    Returns: {"notes": [{"note": "...", "date": "..."}]} or {"notes": []} if none saved.
    """
    if not NOTES_FILE.exists():
        return {"notes": []}
    data = json.loads(NOTES_FILE.read_text())
    return {"notes": data.get(track, {}).get(category, [])}


@mcp.tool()
def get_quiz_problem() -> dict[str, Any]:
    """
    Pick a completed algo problem for the daily pop quiz.
    Weighted toward problems whose pattern_tags appear in weak areas or decayed.
    Avoids repeating the last quiz problem.

    Returns full problem data including answer fields — the agent must NOT reveal
    category, pattern_tags, or optimal complexity until after the user answers.
    """
    import random
    data = _load()

    ip = data.get("in_progress")
    if ip:
        start = datetime.fromisoformat(ip["start_time"])
        age_hours = (datetime.now(timezone.utc) - start).total_seconds() / 3600
        if age_hours <= 2:
            return {"session_active": True, "in_progress": ip}

    completed = data.get("completed_problem_ids", [])
    if not completed:
        return {"error": "No completed problems yet — solve some algo problems first!"}

    last_quiz_id = data.get("last_quiz_id")
    pool: list[tuple[str, dict]] = []

    for pid in completed:
        if pid == last_quiz_id:
            continue
        try:
            prob = json.load(open(DATA_DIR / "algo" / f"{pid}.json"))
            pool.append((pid, prob))
        except Exception:
            pass

    if not pool:
        return {"error": "No eligible completed problems."}

    pid, prob = random.choice(pool)

    # Save last_quiz_id to avoid immediate repeat tomorrow
    data["last_quiz_id"] = pid
    _save(data)

    return {
        "id": pid,
        "title": prob.get("title", pid),
        "difficulty": prob.get("difficulty", "unknown"),
        "description": prob.get("description", ""),
        "test_cases": prob.get("test_cases", [])[:1],
        # Answer — shown only AFTER user responds
        "answer": {
            "category": prob.get("category", ""),
            "pattern_tags": prob.get("pattern_tags", prob.get("tags", [])),
            "optimal_time": prob.get("optimal_time", ""),
            "optimal_space": prob.get("optimal_space", ""),
        },
    }


@mcp.tool()
def get_lang_quiz_problem() -> dict[str, Any]:
    """
    Pick the next language quiz question in difficulty order: easy → intermediate → hard.
    Tracks completed lang quiz IDs so questions aren't repeated until all are done.
    Returns the full question so the agent can present it to Mayu.
    The 'answer' field must NOT be revealed until after Mayu responds.

    Returns: id, language, topic, subtopic, difficulty, format, prompt,
             task OR code (depending on format), answer (reveal after response).
    """
    import random
    data = _load()

    ip = data.get("in_progress")
    if ip:
        start = datetime.fromisoformat(ip["start_time"])
        age_hours = (datetime.now(timezone.utc) - start).total_seconds() / 3600
        if age_hours <= 2:
            return {"session_active": True, "in_progress": ip}

    lang_quiz_dir = DATA_DIR / "language_quiz"
    if not lang_quiz_dir.exists():
        return {"error": "language_quiz/ directory not found — run generate_language_quiz.py first."}

    all_files = sorted(lang_quiz_dir.glob("*.json"))
    if not all_files:
        return {"error": "No language quiz questions found."}

    # Load all questions, filtered to active languages
    active_languages = _lang_quiz_active_languages()
    questions = []
    for f in all_files:
        try:
            q = json.loads(f.read_text())
            if q.get("language") in active_languages:
                questions.append(q)
        except Exception:
            pass

    completed_ids = set(data.get("completed_lang_quiz_ids", []))

    # Difficulty ordering: beginner → intermediate → advanced
    DIFFICULTY_ORDER = ["beginner", "intermediate", "advanced"]
    chosen = None
    for difficulty in DIFFICULTY_ORDER:
        pool = [q for q in questions if q.get("difficulty") == difficulty and q["id"] not in completed_ids]
        if pool:
            chosen = random.choice(pool)
            break

    # All done — reset and start over from beginner
    if chosen is None:
        data["completed_lang_quiz_ids"] = []
        pool = [q for q in questions if q.get("difficulty") == "beginner"]
        if not pool:
            pool = questions
        chosen = random.choice(pool)

    # Only track last_id here; completed_lang_quiz_ids is updated in log_attempt when track=="lang"
    data["last_lang_quiz_id"] = chosen["id"]
    _save(data)

    # Return full question — agent reveals 'answer' only after Mayu responds
    return chosen


@mcp.tool()
def get_last_completed(track: str) -> dict[str, Any] | None:
    """
    Return the most recently completed item for a track, with title.
    Used by evening drill to review the last-completed GoF pattern.
    Returns {"id": "gof_003", "title": "Abstract Factory"} or null if none completed.
    """
    _validate_track(track)
    data = _load()
    fields = TRACK_FIELDS[track]
    completed = data.get(fields["completed"], [])
    if not completed:
        return None
    last_id = completed[-1]
    return {"id": last_id, "title": _get_title(track, last_id)}


@mcp.tool()
def get_evening_drill() -> dict[str, Any]:
    """
    Return GoF pattern for the evening drill.
    - If a session is currently in progress (in_progress != null), returns session_active: true — drill should be skipped.
    - Otherwise returns the last-completed GoF pattern for review (is_review: true),
      falling back to next-in-queue if nothing completed yet (is_review: false).
    - Includes full pattern content so no further tool calls are needed.
    """
    data = _load()

    # Skip if session in progress (within 2h timeout)
    ip = data.get("in_progress")
    if ip:
        start = datetime.fromisoformat(ip["start_time"])
        age_hours = (datetime.now(timezone.utc) - start).total_seconds() / 3600
        if age_hours <= 2:
            return {"session_active": True, "in_progress": ip}

    fields = TRACK_FIELDS["gof"]
    completed_list = data.get(fields["completed"], [])
    completed_set = set(completed_list)
    postponed = data.get(fields["postponed"], [])

    # Only drill on completed patterns — never preview an unstarted one
    if not completed_list:
        return {"session_active": False, "no_completed": True}

    # Rotate across completed patterns — avoid repeating last drill
    import random
    last_drill_id = data.get("last_drill_id")
    candidates = [pid for pid in completed_list if pid != last_drill_id]
    if not candidates:
        candidates = completed_list  # only one pattern done — use it
    drill_id = random.choice(candidates)

    data["last_drill_id"] = drill_id

    try:
        pattern = json.load(open(DATA_DIR / "gof" / f"{drill_id}.json"))
    except Exception as e:
        return {"error": str(e)}

    # Track question progress per pattern: sequential, shuffle after full cycle, timestamps on each
    import random as _random
    today = _today_pst()
    all_questions = pattern.get("questions", [])
    n = len(all_questions)
    drill_progress = data.setdefault("drill_progress", {})
    state = drill_progress.get(drill_id, {
        "order": list(range(n)),   # current cycle order (shuffled after each cycle)
        "cycle_asked": [],         # indices asked in current cycle (no timestamps needed here)
        "history": [],             # full history: [{index, asked_on}]
    })

    # Sanitize indices against current question count
    state["order"] = [i for i in state["order"] if i < n]
    state["cycle_asked"] = [i for i in state["cycle_asked"] if i < n]
    # Ensure all indices are represented in order
    missing = [i for i in range(n) if i not in state["order"]]
    state["order"].extend(missing)

    # Find next 3 in cycle order not yet asked this cycle
    remaining = [i for i in state["order"] if i not in state["cycle_asked"]]
    if len(remaining) < 3:
        # Cycle complete — reshuffle for next round
        new_order = list(range(n))
        _random.shuffle(new_order)
        state["order"] = new_order
        state["cycle_asked"] = []
        remaining = new_order[:]

    selected_indices = remaining[:3]
    state["cycle_asked"].extend(selected_indices)
    for idx in selected_indices:
        state["history"].append({"index": idx, "asked_on": today})

    drill_progress[drill_id] = state
    data["drill_progress"] = drill_progress
    _save(data)

    questions_for_tonight = [all_questions[i] for i in selected_indices]

    return {
        "id": drill_id,
        "is_review": True,
        "session_active": False,
        "pattern": pattern,
        "questions_for_tonight": questions_for_tonight,
    }


@mcp.tool()
def get_today_activity() -> dict[str, Any]:
    """
    Return everything Mayu completed today (PST), grouped by track.
    Reads attempts.json and filters by today's PST date (converts UTC timestamps).
    Deduplicates by (track, item_id) — keeps first attempt of the day per item.
    Use for end-of-day wrap-up and "what did I do today?" queries.

    Returns:
      {
        "date": "2026-03-21",
        "items": [
          {"track": "algo", "id": "nc_019", "title": "Minimum Window Substring",
           "scores": {...}, "composite_score": 4.2, "time": "21:23"},
          ...
        ],
        "summary": {"algo": 2, "sql": 1, ...}
      }
    """
    today = _today_pst()
    if not ATTEMPTS_FILE.exists():
        return {"date": today, "items": [], "summary": {}}

    raw = json.loads(ATTEMPTS_FILE.read_text())
    attempt_list = raw.get("attempts", [])

    # Determine PST offset from UTC (UTC-8 Nov-Mar, UTC-7 Mar-Oct)
    # Use -7 as a safe approximation for DST months (Mar-Oct)
    pst_offset = timedelta(hours=-7)

    seen: set[tuple[str, str]] = set()
    items = []
    summary: dict[str, int] = {}

    for attempt in attempt_list:
        # Support both old format (problem_id/date) and new format (item_id/timestamp)
        ts_raw = attempt.get("timestamp") or attempt.get("date", "")
        track = attempt.get("track", "")
        item_id = attempt.get("item_id") or attempt.get("problem_id", "")

        if not ts_raw or not item_id:
            continue

        try:
            dt_utc = datetime.fromisoformat(ts_raw)
            if dt_utc.tzinfo is None:
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            dt_pst = dt_utc + pst_offset
            attempt_date = dt_pst.strftime("%Y-%m-%d")
            time_str = dt_pst.strftime("%H:%M")
        except Exception:
            continue

        if attempt_date != today:
            continue

        # Deduplicate — keep first attempt of the day per item
        key = (track, item_id)
        if key in seen:
            continue
        seen.add(key)

        title = _get_title(track, item_id) if track and item_id else item_id
        items.append({
            "track": track,
            "id": item_id,
            "title": title,
            "scores": attempt.get("scores", {}),
            "composite_score": attempt.get("composite_score"),
            "time": time_str,
        })
        summary[track] = summary.get(track, 0) + 1

    items.sort(key=lambda x: x["time"])
    return {"date": today, "items": items, "summary": summary}


@mcp.tool()
def get_progress_report() -> dict[str, Any]:
    """
    Return all stats and completed counts for the progress report card.
    Single call — no further tool calls needed.
    """
    data = _load()
    return {
        "streak_days":      data.get("streak_days", 0),
        "last_active_date": data.get("last_active_date"),
        "stats":            data.get("stats", {}),
        "completed_counts": {
            "algo":          len(data.get("completed_problem_ids", [])),
            "sql":           len(data.get("completed_sql_ids", [])),
            "gof":           len(data.get("completed_pattern_ids", [])),
            "aiml":          len(data.get("completed_concept_ids", [])),
            "behavioral":    len(data.get("completed_behavioral_ids", [])),
            "system_design": len(data.get("completed_design_ids", [])),
            "nc_core":       len(data.get("completed_core_ids", [])),
            "ds":            len(data.get("completed_ds_ids", [])),
        },
        "quiz_today_count": (
            data.get("quiz_today_count", 0)
            if data.get("quiz_today_date") == _today_pst()
            else 0
        ),
        "quiz_week_count": (
            data.get("quiz_week_count", 0)
            if data.get("quiz_week_start") == _week_start_pst()
            else 0
        ),
    }


@mcp.tool()
def start_track(track: str) -> dict[str, Any]:
    """
    Start or resume a session for the given track. Single call replaces:
      get_in_progress + get_next_items + set_in_progress

    Returns:
      {
        "id": "sql_001",
        "title": "Combine Two Tables",
        "postponed": false,
        "is_resume": false   # true if resuming an in-progress item
      }

    The agent should call the relevant content tool next (get_sql_problem, get_problem, etc.)
    using the returned id, then output immediately.
    """
    _validate_track(track)
    data = _load()

    # Check for active resume (only if session < 2h old)
    ip = data.get("in_progress")
    if ip and ip.get("track") == track:
        start = datetime.fromisoformat(ip["start_time"])
        age_hours = (datetime.now(timezone.utc) - start).total_seconds() / 3600
        if age_hours <= 2:
            item_id = ip["id"]
            return {
                "id": item_id,
                "title": _get_title(track, item_id),
                "postponed": False,
                "is_resume": True,
            }

    # Get next item in queue
    fields = TRACK_FIELDS[track]
    completed = set(data.get(fields["completed"], []))
    postponed = data.get(fields["postponed"], [])
    sequence = SEQUENCES[track]

    item_id = None
    is_postponed = False
    for pid in postponed:
        item_id = pid
        is_postponed = True
        break
    if not item_id:
        for pid in sequence:
            if pid not in completed and pid not in set(postponed):
                item_id = pid
                break

    if not item_id:
        return {"error": f"All {track} items completed!"}

    # Set in_progress
    data["in_progress"] = {
        "track": track,
        "id": item_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
    }
    _save(data)

    return {
        "id": item_id,
        "title": _get_title(track, item_id),
        "postponed": is_postponed,
        "is_resume": False,
    }


@mcp.tool()
def get_next_items(track: str, n: int = 1) -> list[dict[str, Any]]:
    """
    Return next N items for a track in correct queue order.
    Postponed items always come first, then uncompleted items in curriculum order.
    The LLM never needs to calculate this — just call this tool.

    Args:
        track: one of "algo", "sql", "gof", "aiml", "behavioral", "system_design"
        n: number of items to return (default 1)

    Returns list of {"id": "nc_015", "postponed": false}
    """
    _validate_track(track)
    data = _load()
    fields = TRACK_FIELDS[track]
    completed  = set(data.get(fields["completed"], []))
    postponed  = data.get(fields["postponed"], [])
    sequence   = SEQUENCES[track]

    result: list[dict[str, Any]] = []

    # 1. Postponed items first
    for pid in postponed:
        if len(result) >= n:
            break
        result.append({"id": pid, "postponed": True})

    # 2. Fill remaining slots from sequence
    assigned = {r["id"] for r in result}
    for item_id in sequence:
        if len(result) >= n:
            break
        if item_id not in completed and item_id not in assigned:
            result.append({"id": item_id, "postponed": False})

    return result


@mcp.tool()
def set_in_progress(track: str, id: str) -> dict[str, str]:
    """
    Mark an item as currently in progress.
    Call this when you present a problem to the user.

    Args:
        track: track name (e.g. "algo")
        id: item ID (e.g. "nc_015")
    """
    _validate_track(track)
    data = _load()
    data["in_progress"] = {
        "track": track,
        "id": id,
        "start_time": datetime.now(timezone.utc).isoformat(),
    }
    _save(data)
    return {"ok": "true", "in_progress": id}


@mcp.tool()
def get_in_progress() -> dict[str, Any] | None:
    """
    Return the currently in-progress item, or null if none.
    Call on session resume to avoid re-presenting a problem already shown.
    """
    data = _load()
    return data.get("in_progress")


@mcp.tool()
def clear_in_progress() -> dict[str, Any]:
    """
    Cancel the current in-progress session without recording an attempt.
    Use when Mayu explicitly cancels (/cancel) or abandons a problem.
    Returns the cleared item so the agent can confirm what was cancelled.
    """
    data = _load()
    ip = data.get("in_progress")
    if not ip:
        return {"ok": True, "cleared": None, "message": "No session was in progress."}
    data["in_progress"] = None
    _save(data)
    return {"ok": True, "cleared": ip}


@mcp.tool()
def add_completed(track: str, id: str, within_time_limit: bool | None = None) -> dict[str, Any]:
    """
    Mark an item as completed. Atomically:
    - Appends id to completed_*_ids
    - Increments the relevant stats counter
    - Updates last_active_date and streak
    - Removes id from postponed_*_ids if present
    - Clears in_progress if it matches this item

    ONLY these fields are modified — all other fields are preserved exactly.

    Args:
        track: track name
        id: item ID
        within_time_limit: for timed mocks only — pass the result from stop_timer()
            (true = stopped before expiry, false = timer already fired, null = not timed)

    Returns updated stats including elapsed_display and within_time_limit.
    """
    _validate_track(track)
    data  = _load()
    today = _today_pst()
    fields = TRACK_FIELDS[track]

    # Add to completed (idempotent — only increment stat on first completion)
    completed_list = data.setdefault(fields["completed"], [])
    already_done = id in completed_list
    if not already_done:
        completed_list.append(id)
        # Increment stat only on first completion
        stat_key = fields["stat"]
        if stat_key:
            data.setdefault("stats", {})[stat_key] = data["stats"].get(stat_key, 0) + 1

    # Streak + last_active_date
    _update_streak(data, today)

    # Remove from postponed
    postponed_list = data.setdefault(fields["postponed"], [])
    if id in postponed_list:
        postponed_list.remove(id)

    # Clear in_progress if it matches; capture elapsed time
    elapsed_seconds = None
    ip = data.get("in_progress")
    if ip and ip.get("id") == id:
        try:
            start = datetime.fromisoformat(ip["start_time"])
            elapsed_seconds = int((datetime.now(timezone.utc) - start).total_seconds())
        except Exception:
            pass
        data["in_progress"] = None

    # Clean up any stale timer file (stop_timer should have cleared it already for timed mocks)
    TIMER_FILE.unlink(missing_ok=True)

    # Weekly goal tracking (algo, sql, gof, aiml only)
    if track in WEEKLY_GOALS and not already_done:
        _check_week_reset(data, today)
        wc = data.setdefault("week_completions", {k: 0 for k in WEEKLY_GOALS})
        wc[track] = wc.get(track, 0) + 1

    _save(data)
    result: dict[str, Any] = {"ok": "true", "stats": data.get("stats", {})}
    if elapsed_seconds is not None:
        result["elapsed_seconds"] = elapsed_seconds
        m, s = divmod(elapsed_seconds, 60)
        result["elapsed_display"] = f"{m}m {s}s"
    # Pass through within_time_limit from stop_timer() result — agent determines this
    result["within_time_limit"] = within_time_limit
    return result


@mcp.tool()
def complete_item(
    track: str,
    id: str,
    scores: dict[str, int],
    solution: str = "",
    hints_used: int = 0,
    timed_mock: bool = False,
    within_time_limit: bool | None = None,
    is_quiz: bool = False,
) -> dict[str, Any]:
    """
    Atomic completion: marks item done AND records attempt in a single call.
    Replaces the separate add_completed + log_attempt sequence for all tracks
    except behavioral (which also needs save_behavioral_response).

    Also runs get_category_summary for algo items and returns the result inline.

    Args:
        track: track name
        id: item ID
        scores: score dict for the track (same as log_attempt)
        solution: user's submitted code or explanation
        hints_used: number of hints requested
        timed_mock: whether this was a timed mock
        within_time_limit: result from stop_timer (null if not timed)
        is_quiz: true for pop quiz attempts

    Returns: ok, stats, composite_score, review_scheduled, elapsed_display,
             category_summary (algo only, may be None if category not complete).
    """
    completed_result = add_completed(track, id, within_time_limit=within_time_limit)
    attempt_result = log_attempt(
        track=track,
        id=id,
        scores=scores,
        solution=solution,
        hints_used=hints_used,
        timed_mock=timed_mock,
        within_time_limit=within_time_limit,
        is_quiz=is_quiz,
    )
    result: dict[str, Any] = {
        **completed_result,
        "composite_score": attempt_result["composite_score"],
        "review_scheduled": attempt_result.get("review_scheduled"),
        "attempt_id": attempt_result["attempt_id"],
    }
    if track == "algo":
        result["category_summary"] = get_category_summary(track, id)
    return result


@mcp.tool()
def add_postponed(track: str, id: str) -> dict[str, Any]:
    """
    Add an item to the postponed list for its track.
    Enforces max 3 per track. Re-postponing an already-postponed item is a no-op.

    Args:
        track: track name
        id: item ID

    Returns {"ok": true} or {"ok": false, "error": "Backlog full (3/3)"}
    """
    _validate_track(track)
    data = _load()
    fields = TRACK_FIELDS[track]
    postponed_list = data.setdefault(fields["postponed"], [])

    if id in postponed_list:
        return {"ok": "true", "note": "already postponed"}

    if len(postponed_list) >= POSTPONE_LIMIT:
        return {
            "ok": "false",
            "error": f"Backlog full ({POSTPONE_LIMIT}/{POSTPONE_LIMIT}) for {track} — clear it before deferring more.",
        }

    postponed_list.append(id)
    _save(data)
    return {"ok": "true", "postponed_count": len(postponed_list)}


@mcp.tool()
def remove_postponed(track: str, id: str) -> dict[str, Any]:
    """
    Remove an item from the postponed list (e.g. when user clears a backlog item).

    Args:
        track: track name
        id: item ID
    """
    _validate_track(track)
    data = _load()
    fields = TRACK_FIELDS[track]
    postponed_list = data.setdefault(fields["postponed"], [])

    if id in postponed_list:
        postponed_list.remove(id)
        _save(data)
        return {"ok": "true", "removed": id}

    return {"ok": "true", "note": "not in postponed list"}


if __name__ == "__main__":
    mcp.run()
