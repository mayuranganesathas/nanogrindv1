# Nanobot Memory

## User
- Name: Mayu | Timezone: America/Los_Angeles (UTC−7 Mar–Oct, UTC−8 Nov–Feb)
- Preferred languages: JS/TS (algo, SQL), Python (AI/ML)
- Rest day: Sunday (behavioral sessions from wk 8+)
- Role: Senior SWE preparing for top-tier interviews

## Architecture (v2 MCP)
- All progress data accessed via MCP tools — never read progress.json directly
- All problem content accessed via MCP tools — never scan data directories
- Use `start_track(track)` to begin every session — returns next id, handles resume and postponed priority automatically
- Use `get_next_items(track, n)` only when you need to peek ahead (e.g. behavioral 2-question fetch)

## Track names
algo, sql, gof, aiml, behavioral, system_design, nc_core, ds

## AIML label
id starts with `ml_m` → label "Math" | all other ml_ ids → label "AI/ML"

## Schedule
- Start date: 2026-03-17 (Week 1 Day 1)
- Target: 2026-08-15 (~20 weeks total)
- Unlock schedule: System Design wk 6 (Mon–Sat) | Behavioral wk 8 (Sundays only, 3–5 Qs) | AI/ML wk 11

## Weekly targets
- Algo: 12 | SQL: 3 | GoF: 2 | DS: 3 | NC Core: 3
- System Design (wk 6+): 3 | Behavioral (wk 8+): 3–5 on Sunday | AI/ML (wk 11+): 2

## Progress & Stats
- Total problems solved: 26 (as of 2026-03-25)
- Total SQL solved: 5 (sql_001–sql_005)
- Total GoF: 2 (gof_001 Singleton, gof_002 Factory Method)
- Total AI/ML: 1 (ml_m01, ml_m02 postponed)
- **Current In-Progress**: nc_027 (Largest Rectangle in Histogram)
- **Postponed Items**: ml_m02 "Matrices and Linear Transformations"
- **Completed Categories**: Sliding Window (nc_015–nc_020), Stack (nc_021–nc_023, nc_025), GoF (Singleton, Factory Method)

## User Notes & Takeaways
- **Two Pointers**: Frequency maps are important; `.split()`/`.map()` don't need explicit `return` without curly braces; arrays aren't unique keys in Sets/Maps (use stringified tuples); bucket sort is O(n) for top-K frequency problems.
- **SQL Duplicates**: Canonical pattern is `SELECT col FROM table GROUP BY col HAVING COUNT(*) > 1`.
- **SQL Anti-Join**: Use `LEFT JOIN ... WHERE foreign_key IS NULL` or `NOT IN (subquery)` to find records without matches. LEFT JOIN with empty right table returns all left rows, not nothing.
- **Sliding Window (nc_016)**: When a duplicate is found at `right`, shrink from `left` using `while(charSet.has(s[right])) { charSet.delete(s[left]); left++; }`. Calculate window size dynamically via `right - left + 1` rather than maintaining a separate counter.
- **Sliding Window with Replacement (nc_017)**: To find longest substring with at most k replacements, track `max_freq` of any character in the current window. Validity condition: `(window_size - max_freq) <= k`. Replacements needed = characters that are NOT the most frequent one. Tracking `max_freq` avoids O(n²) by not recounting every character's changes individually.
- **Fixed-Size Sliding Window (nc_018)**: For permutation problems, window size is fixed to `s1.length`. Use frequency maps for both `s1` and the current window in `s2`. Slide by adding new char at `right` and removing old char at `left`. Compare maps or use a "matches" counter. Time: O(n * 26) ≈ O(n), Space: O(1).
- **Singleton Pattern (gof_001)**:
  - Implementation requires `__new__` to control instantiation and `__init__` guarded against re-initialization.
  - Thread-safety achieved via double-checked locking (`threading.Lock`).
  - Use cases: Loggers, Config managers, DB connections (expensive/shared resources).
  - Trade-offs: Hard to test due to hidden global state; can become bloated/brittle.
  - **Dependency Injection** preferred for business logic/testability as it allows swapping implementations (mocks vs real) and makes dependencies explicit.
  - **Double-Checked Locking Pattern**: First check `_instance` without lock (performance), then acquire lock, second check with lock (safety) before creating instance. `__new__` controls instantiation; `__init__` must guard against re-initialization.
- **Monotonic Deque (nc_020)**: Used for Sliding Window Maximum/Minimum. Stores indices in decreasing order of values. Front is max. Remove from back if new element > back; remove front if index out of window (`if (deque[0] === r - k)`). Achieves O(n) time by processing each element at most twice. Key insight: `nums[i] < nums[j]` with `i < j` means `nums[i]` can never be max in future windows containing `nums[j]`.
- **Sliding Window General**: Fixed size (k): both pointers move together. Variable size: expand right unconditionally, contract left only when invalid. Use frequency maps for substrings/distinct elements. O(n) guarantee: each element added/removed at most once.
- **Stack Pattern (nc_021)**:
  - Used for "Valid Parentheses" and nested structure validation.
  - Core logic: Map closing brackets to opening (`{')': '(', ...}`); push opening brackets; on closing bracket, check if stack top matches map value, pop if yes, return false if no or empty.
  - Key insight: LIFO order is required because the most recently opened bracket must be closed first (nesting structure). A queue (FIFO) fails because it ignores nesting depth.
  - Complexity: O(n) time (single pass), O(n) space (worst case all opens).
  - Common bug: Pushing closing brackets to stack (only push opens).
- **Min Stack Pattern (nc_022)**:
  - Use auxiliary stack (`minStack`) to track minimum at each level for O(1) `getMin`.
  - **Space Optimization**: Only push to `minStack` if `val <= current_min`; on `pop`, only pop from `minStack` if popped value equals current min.
  - **Critical Edge Case**: Use `<=` instead of `<` when pushing to handle duplicate minimums correctly (ensures count of minimums is tracked).
  - Complexity: Time O(1) for all ops; Space O(n) worst case, O(k) optimized where k = number of min changes.
- **RPN Evaluation Pattern (nc_023)**:
  - Use a single stack to store operands.
  - Iterate tokens: if number → push; if operator → pop 2 values, compute (`second op first` for `-` and `/`), push result.
  - Division truncates toward zero (use `Math.trunc()` or `~~`).
  - Final result is the single value remaining on stack.
  - **Common Mistake**: Do not separate operators into a second stack; process immediately upon encountering an operator.
  - **Why RPN works**: Operators apply to the two most recent operands, encoding evaluation order via position rather than parentheses.
- **SQL Conditional Aggregation (sql_004)**: Pattern `CASE WHEN condition1 AND condition2 THEN value ELSE 0 END`. Common in bonuses/tiers. Ensure `ORDER BY` if required. Use `NOT LIKE 'X%'` for exclusion.
- **SQL Filtering Syntax (sql_005)**: Always use SQL keywords (`AND`, `OR`) not programming operators (`&&`, `||`). Match data types: integers without quotes, strings with single quotes. Filter by year explicitly when needed.
- **Factory Method Pattern (gof_002)**:
  - Defers instantiation of objects to subclasses; abstract creator defines interface, concrete creators implement specific creation logic.
  - Use cases: UI frameworks (extensible input types), logging, payment processing.
  - Trade-offs: Class explosion (one class per product type), overlapping behavior management, testing complexity (each subclass needs tests).
  - **When to avoid**: Few product types, no third-party extensions, simple logic better handled by a factory function.
  - **Key Distinction vs Simple Factory**: Simple factory is a static method/function modified to add types; Factory Method uses inheritance to create new subclasses for new types (Open/Closed Principle).
  - **Concrete Example**: `UIComponentCreator` base class with `createInput()` abstract method; subclasses like `ButtonCreator`, `TextBoxCreator` return specific UI elements. Allows third-party plugins to extend without touching core code.
  - **Pitfalls**: Overhead of maintaining many subclasses, tight coupling to inheritance hierarchy where composition might be better.
- **Generate Parentheses (nc_024)**:
  - **Pattern**: Backtracking with constraints (Catalan number pattern).
  - **Space Optimization**: Streaming results (e.g., `console.log` or `yield`) reduces space complexity from O(4^n) to O(n) (recursion stack only), at the cost of not being able to reuse/return all results.
  - **Key Constraints**: Add '(' if `open < n`; add ')' if `close < open`.
  - **Complexity**: Time O(4^n / √n), Space O(n) for streaming, O(result_count) for storing.
- **Monotonic Stack (nc_025 "Daily Temperatures")**:
  - **Pattern**: Store indices in decreasing order of values (temperatures). When a warmer day is found, pop cooler days and calculate wait time (`current_index - popped_index`).
  - **Key Insight**: A cooler day `i` can never be the answer for any future day if a warmer day `j` exists between them; thus, we only need to track indices where no warmer day has been found yet.
  - **Implementation**: Iterate through temperatures; while stack top temp < current temp, pop and set result index; push current index. Initialize result array with zeros (or handle remaining stack).
  - **Complexity**: Time O(N) (each element pushed/popped at most once), Space O(N) for stack and result array.
  - **Common Pitfall**: Using `push` to append results instead of direct assignment `result[index] = value`.
  - **Terminology**: Must be called a "stack", not "deque", as operations are only on one end.
- **Car Fleet Pattern (nc_026)**:
  - **Pattern**: Sort by position descending, calculate float time-to-target `(target - pos) / speed`. Track `max_time` seen so far.
  - **Logic**: If current car's time ≤ `max_time`, it catches up to the fleet ahead (join). If time > `max_time`, it forms a new fleet and updates `max_time`.
  - **Complexity**: O(N log N) due to sorting; O(1) extra space if sorting in-place.
  - **Key Insight**: A car can only catch up to cars *ahead* of it. Processing from closest to target ensures we know the "leader" fleet's arrival time.
  - **Common Mistake**: Losing position-to-speed mapping when calculating times; using integer division instead of float; processing in wrong order.
- **Largest Rectangle in Histogram (nc_027)**:
  - **Pattern**: Monotonic Increasing Stack (indices).
  - **Core Logic**: Maintain stack of indices with increasing heights. When current bar < stack top: pop index `h_idx`. Right boundary = current index `i`. Left boundary = new stack top (or -1 if empty). Width = `right - left - 1`. Area = `heights[h_idx] * width`.
  - **Extension Rule**: A rectangle anchored at height `H` extends left/right as long as bars are **≥ H** (includes equal heights).
  - **Brute Force**: O(n²) by expanding left/right from each bar.
  - **Optimal Complexity**: O(n) time (each element pushed/popped once), O(n) space.
  - **Key Insight**: Popping a bar reveals its right boundary (first smaller bar to the right) and the new stack top reveals its left boundary (first smaller bar to the left).
