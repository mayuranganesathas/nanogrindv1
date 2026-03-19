#!/usr/bin/env python3
"""Generate conceptual SQL questions sql_051–sql_065 on the VM.
Covers views, materialized views, indexes, ACID, isolation levels,
normalization, CTEs, EXPLAIN, partitioning, sharding, N+1, OLAP, star schema.
"""
import json
from pathlib import Path

OUT = Path("/mnt/c/Users/U/Documents/nanogrindv2/data_generated/sql")
OUT.mkdir(exist_ok=True)

QUESTIONS = [
    {
        "id": "sql_051",
        "difficulty": "Medium",
        "category": "CONCEPTS / VIEWS",
        "is_conceptual": True,
        "title": "Database Views — What They Are and When to Use Them",
        "description": "Explain what a database VIEW is. What are the benefits and limitations of views? When would you create one?",
        "key_concept": "A view is a stored query — a virtual table that presents data without storing it. Benefits: abstraction, security, simplification. Limitation: no separate storage, no index on view itself (in most DBs).",
        "hints": {
            "L1": "A view is like a saved SELECT statement. When you query it, the underlying query runs. How does that differ from a real table?",
            "L2": "Views: (1) hide complexity behind a simple name, (2) restrict column/row access for security, (3) present data in a different shape. But they rerun the query every time — no caching.",
            "L3": "CREATE VIEW active_users AS SELECT id, name, email FROM users WHERE deleted_at IS NULL;\n-- Now: SELECT * FROM active_users; -- runs the subquery every time\n-- Benefits: abstraction (callers don't know about deleted_at), security (can GRANT on view, not table), DRY (write complex join once).\n-- Limitations: can't always UPDATE through views (depends on DB/complexity), no indexes on the view result, performance same as running query directly."
        },
        "optimal_solution": "A VIEW is a named, stored query — when you SELECT from a view, the DB runs the underlying query.\n\nBenefits:\n  1. Abstraction: hide joins/filters behind a simple name\n  2. Security: GRANT SELECT on the view (not the base table) to restrict column/row access\n  3. DRY: define complex business logic once, reuse everywhere\n  4. Backward compatibility: change table structure, keep view interface stable\n\nLimitations:\n  - No separate storage — data not cached, query reruns each time\n  - Performance same as inline query (no magic optimization)\n  - Updatable only under specific conditions (simple single-table views)\n\nExample:\nCREATE VIEW customer_summary AS\n  SELECT c.id, c.name, COUNT(o.id) AS order_count, SUM(o.total) AS lifetime_value\n  FROM customers c\n  LEFT JOIN orders o ON o.customer_id = c.id\n  GROUP BY c.id, c.name;\n\nSELECT * FROM customer_summary WHERE lifetime_value > 1000;"
    },
    {
        "id": "sql_052",
        "difficulty": "Hard",
        "category": "CONCEPTS / VIEWS",
        "is_conceptual": True,
        "title": "Materialized Views — How They Differ from Regular Views",
        "description": "What is a MATERIALIZED VIEW and how does it differ from a regular view? What are the refresh strategies and when would you use one over a regular view?",
        "key_concept": "A materialized view physically stores the query result — it's a cached snapshot. Faster reads, but data can be stale. Used for expensive aggregations in reporting/analytics.",
        "hints": {
            "L1": "Unlike a regular view (reruns query each time), a materialized view stores the result set on disk. What trade-off does this introduce?",
            "L2": "Refresh strategies: COMPLETE (full rebuild), FAST (incremental using logs), ON COMMIT (refresh when base table changes), ON DEMAND (manual refresh). PostgreSQL: REFRESH MATERIALIZED VIEW.",
            "L3": "Use materialized views when: (1) the query is expensive (heavy aggregations, many joins), (2) you can tolerate slightly stale data, (3) read performance is critical. Common in analytics, dashboards, reporting pipelines."
        },
        "optimal_solution": "A MATERIALIZED VIEW (mat view) physically stores the query result as a table-like structure on disk.\n\nVs Regular View:\n  Regular view: virtual, reruns query on every SELECT (always fresh, always full cost)\n  Materialized view: stored snapshot, reads are instant, but data goes stale until refreshed\n\nRefresh strategies:\n  ON COMMIT: auto-refresh when underlying tables change (keeps data fresh, adds write latency)\n  ON DEMAND: refresh manually or on a schedule (e.g., nightly REFRESH MATERIALIZED VIEW)\n  INCREMENTAL/FAST: only apply changes since last refresh (requires change-tracking logs)\n\nPostgreSQL syntax:\n  CREATE MATERIALIZED VIEW monthly_sales AS\n    SELECT DATE_TRUNC('month', created_at) AS month,\n           SUM(total) AS revenue,\n           COUNT(*) AS orders\n    FROM orders\n    GROUP BY 1;\n\n  REFRESH MATERIALIZED VIEW monthly_sales; -- run nightly via cron\n\nWhen to use:\n  - Expensive aggregations (SUM over millions of rows) needed frequently\n  - Analytics dashboards where 1-hour stale data is acceptable\n  - Reports that run slowly because of complex multi-table joins\n  - Read-heavy systems where the base data changes infrequently\n\nBenefits: Can CREATE INDEX ON the materialized view — massive speedup for filtered reads."
    },
    {
        "id": "sql_053",
        "difficulty": "Medium",
        "category": "CONCEPTS / INDEXES",
        "is_conceptual": True,
        "title": "Clustered vs Non-Clustered Indexes",
        "description": "What is the difference between a clustered and a non-clustered index? How does each affect storage, read performance, and write performance?",
        "key_concept": "Clustered index: rows physically sorted by index key (one per table, usually PK). Non-clustered: separate structure with pointers to rows. Clustered = faster range reads; non-clustered = more flexible but extra lookup.",
        "hints": {
            "L1": "A clustered index changes the physical order of rows. A table can only have ONE clustered index — why?",
            "L2": "Clustered index (SQL Server/MySQL InnoDB): rows stored in B-tree leaf pages sorted by the key. Range scans (WHERE date BETWEEN x AND y) are fast because data is contiguous. Non-clustered: separate B-tree, leaf nodes store the key + a pointer (row ID or cluster key) to the actual row.",
            "L3": "Non-clustered lookup: find key in index B-tree → follow pointer to heap/clustered page → read row. This double lookup is called a 'key lookup' or 'bookmark lookup'. A COVERING INDEX eliminates this: include all needed columns in the index so no row lookup is needed."
        },
        "optimal_solution": "Clustered Index:\n  - Rows in the table ARE the index — physically sorted by the key in B-tree leaf pages\n  - Only ONE per table (physical ordering constraint)\n  - Usually the primary key (InnoDB creates it automatically)\n  - Fast: range scans, ORDER BY on the key, equality lookups\n  - All non-clustered indexes store the cluster key as their pointer\n\nNon-Clustered Index:\n  - Separate B-tree structure; leaf nodes = (index key, pointer to row)\n  - Multiple per table allowed\n  - Range scan on index, then 'key lookup' to fetch full row (two reads)\n  - Covering index: include extra columns to eliminate the key lookup\n\nExample:\n  -- Clustered (implicit on PK in PostgreSQL/MySQL):\n  CREATE TABLE orders (id BIGINT PRIMARY KEY, ...); -- clustered on id\n\n  -- Non-clustered:\n  CREATE INDEX idx_orders_customer ON orders(customer_id);\n\n  -- Covering index (include total so no row lookup for this query):\n  CREATE INDEX idx_orders_covering ON orders(customer_id) INCLUDE (total, created_at);\n  -- SELECT total, created_at FROM orders WHERE customer_id = 42 → index-only scan\n\nWrite impact: every INSERT/UPDATE/DELETE must update all indexes — too many indexes slow writes."
    },
    {
        "id": "sql_054",
        "difficulty": "Hard",
        "category": "CONCEPTS / INDEXES",
        "is_conceptual": True,
        "title": "Index Strategy — When Indexes Help vs Hurt",
        "description": "What factors determine whether an index will actually be used by the query planner? When do indexes hurt performance? Explain composite indexes and the 'left-prefix rule'.",
        "key_concept": "Indexes are skipped for low-selectivity columns, functions on columns, and small tables. Composite indexes must be used left-to-right. Too many indexes hurt write performance.",
        "hints": {
            "L1": "The query planner uses statistics to decide whether a full table scan is cheaper than an index lookup. When might scanning be faster than using an index?",
            "L2": "Index skipped when: low cardinality (e.g., boolean column — index skips 50% of rows at best), function applied to column (WHERE YEAR(created_at) = 2025 prevents index use on created_at), implicit cast, small table (full scan faster).",
            "L3": "Composite index (a, b, c): usable for: WHERE a=1, WHERE a=1 AND b=2, WHERE a=1 AND b=2 AND c=3. NOT usable for: WHERE b=2 alone, WHERE c=3 alone. Range condition on a 'stops' the prefix: WHERE a=1 AND b>5 AND c=3 — c is not using the index."
        },
        "optimal_solution": "When indexes are NOT used:\n  1. Low selectivity: `WHERE is_active = TRUE` — if 80% of rows are active, full scan is faster\n  2. Function on column: `WHERE YEAR(created_at) = 2025` → optimizer can't use index on created_at\n     Fix: `WHERE created_at BETWEEN '2025-01-01' AND '2025-12-31'`\n  3. Leading wildcard: `WHERE name LIKE '%smith'` (can't seek from left)\n  4. Implicit type cast: `WHERE user_id = '123'` when user_id is INT\n  5. Very small tables: sequential scan is cheaper than index overhead\n\nComposite index left-prefix rule:\n  INDEX ON (a, b, c)\n  ✓ WHERE a = 1\n  ✓ WHERE a = 1 AND b = 2\n  ✓ WHERE a = 1 AND b = 2 AND c = 3\n  ✓ WHERE a = 1 AND b BETWEEN 5 AND 10 (but c not usable)\n  ✗ WHERE b = 2 (skips a)\n  ✗ WHERE c = 3 (skips a and b)\n\nIndex hurts performance:\n  - Every write (INSERT/UPDATE/DELETE) updates all indexes\n  - Indexes consume disk space\n  - Stale statistics can cause bad query plans\n  - Too many indexes → optimizer spends time choosing among them\n\nRule of thumb: index foreign keys, high-cardinality filter columns, sort columns. Avoid indexing columns rarely used in WHERE/JOIN."
    },
    {
        "id": "sql_055",
        "difficulty": "Medium",
        "category": "CONCEPTS / TRANSACTIONS",
        "is_conceptual": True,
        "title": "ACID Properties",
        "description": "Explain the four ACID properties of database transactions. Give a concrete example showing why each property matters.",
        "key_concept": "Atomicity (all-or-nothing), Consistency (valid state to valid state), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes).",
        "hints": {
            "L1": "ACID stands for: Atomicity, Consistency, Isolation, Durability. Think of a bank transfer: debit one account, credit another. Which property ensures both happen or neither does?",
            "L2": "Atomicity: both debit + credit succeed or both roll back. Consistency: can't leave balance negative if constrained. Isolation: two concurrent transfers don't see each other's intermediate state. Durability: once committed, a server crash doesn't lose the data.",
            "L3": "Implementation: Atomicity via transaction log (undo on rollback). Consistency via constraints + triggers. Isolation via locking or MVCC. Durability via write-ahead log (WAL) — changes logged to disk before confirming commit."
        },
        "optimal_solution": "ACID — the four guarantees of a reliable transaction:\n\n1. ATOMICITY — all or nothing\n   Bank transfer: debit $100 from A, credit $100 to B.\n   If step 2 fails (crash, constraint violation), step 1 is rolled back.\n   No partial transactions: money can't disappear into limbo.\n\n2. CONSISTENCY — valid state → valid state\n   DB constraints (NOT NULL, FOREIGN KEY, CHECK) are enforced.\n   A transfer can't leave an account with a negative balance if there's a CHECK constraint.\n   The DB goes from one 'consistent' state to another.\n\n3. ISOLATION — concurrent transactions don't interfere\n   Two transfers happening simultaneously don't see each other's mid-flight changes.\n   Without isolation: T1 reads $100, T2 reads $100, both spend $100 — total $200 spent from $100.\n   Isolation level controls HOW isolated (READ COMMITTED, SERIALIZABLE, etc.).\n\n4. DURABILITY — committed = permanent\n   After COMMIT, the data survives: power failure, OS crash, disk flush.\n   Implemented via Write-Ahead Log (WAL): changes written to log before data pages.\n   On recovery, replays WAL to restore committed state.\n\nBEGIN;\n  UPDATE accounts SET balance = balance - 100 WHERE id = 1;\n  UPDATE accounts SET balance = balance + 100 WHERE id = 2;\nCOMMIT; -- both committed atomically"
    },
    {
        "id": "sql_056",
        "difficulty": "Hard",
        "category": "CONCEPTS / TRANSACTIONS",
        "is_conceptual": True,
        "title": "Isolation Levels — Dirty Reads, Phantom Reads, Non-Repeatable Reads",
        "description": "What are the four SQL isolation levels? What read anomalies does each prevent? When would you choose SERIALIZABLE vs READ COMMITTED?",
        "key_concept": "READ UNCOMMITTED → dirty reads. READ COMMITTED → no dirty reads. REPEATABLE READ → no non-repeatable reads. SERIALIZABLE → no phantom reads. Higher isolation = more locking/blocking.",
        "hints": {
            "L1": "Three read anomalies: (1) dirty read — reading uncommitted data from another transaction, (2) non-repeatable read — same row returns different data on second read, (3) phantom read — same query returns different rows on second read.",
            "L2": "READ UNCOMMITTED: allows all three. READ COMMITTED (default in PostgreSQL): prevents dirty reads. REPEATABLE READ (default in MySQL InnoDB): prevents dirty + non-repeatable. SERIALIZABLE: prevents all three — full isolation, slowest.",
            "L3": "Most apps use READ COMMITTED. Use REPEATABLE READ for multi-step reads in one transaction (e.g., balance check then transfer). Use SERIALIZABLE for critical financial workflows where phantom reads could cause double-booking. MVCC (Multi-Version Concurrency Control) implements isolation without locking reads."
        },
        "optimal_solution": "Anomalies:\n  Dirty read: T1 reads data that T2 modified but not yet committed. T2 rolls back — T1 read phantom data.\n  Non-repeatable read: T1 reads row, T2 updates + commits it, T1 reads same row again — different result.\n  Phantom read: T1 queries a range, T2 inserts a row in that range + commits, T1 queries again — new row appears.\n\nIsolation levels (SQL standard):\n  READ UNCOMMITTED: allows dirty reads, non-repeatable, phantom. Fastest, rarely used.\n  READ COMMITTED:   prevents dirty reads. Still allows non-repeatable + phantom. Default in PG, Oracle.\n  REPEATABLE READ:  prevents dirty + non-repeatable. Still allows phantom. Default in MySQL InnoDB (InnoDB uses gap locks to prevent phantom too).\n  SERIALIZABLE:     prevents all three. Full isolation — transactions behave as if run serially. Slowest.\n\nSET TRANSACTION ISOLATION LEVEL SERIALIZABLE;\nBEGIN;\n  SELECT SUM(balance) FROM accounts WHERE user_id = 42; -- snapshot locked\n  -- another transaction can't insert a new account for user 42 in this range\nCOMMIT;\n\nPractical guidance:\n  READ COMMITTED: most web apps — good balance of performance and safety.\n  REPEATABLE READ: reports that read the same data multiple times in one transaction.\n  SERIALIZABLE: financial double-booking prevention, seat reservations, ticket systems."
    },
    {
        "id": "sql_057",
        "difficulty": "Medium",
        "category": "CONCEPTS / DESIGN",
        "is_conceptual": True,
        "title": "Database Normalization — 1NF through 3NF",
        "description": "Explain 1NF, 2NF, and 3NF normalization. What problems does each level solve? When is denormalization appropriate?",
        "key_concept": "1NF: atomic values, no repeating groups. 2NF: no partial dependencies (all cols depend on full PK). 3NF: no transitive dependencies (non-key cols don't depend on other non-key cols).",
        "hints": {
            "L1": "Normalization reduces data redundancy and update anomalies. 1NF is the starting point — what does 'atomic values' mean?",
            "L2": "1NF violation: storing 'tags' as a comma-separated string in one column. 2NF violation: composite PK (order_id, product_id) but product_name depends only on product_id. 3NF violation: storing both zip_code and city in orders — city depends on zip_code, not the order.",
            "L3": "Denormalize when: read performance is critical and data is rarely updated, analytics/reporting (star schema is intentionally denormalized), avoiding expensive JOINs at query time. Trade-off: faster reads, harder updates, potential inconsistency."
        },
        "optimal_solution": "1NF (First Normal Form): No repeating groups, atomic values\n  Violation: orders.tags = 'urgent,fragile,cold'  ← not atomic\n  Fix: order_tags(order_id, tag) table\n\n2NF (Second Normal Form): No partial dependencies\n  Only applies when PK is composite.\n  Violation: order_items(order_id, product_id, quantity, product_name)\n    product_name depends on product_id alone — not the full PK.\n  Fix: move product_name to a products table.\n\n3NF (Third Normal Form): No transitive dependencies\n  Violation: employees(emp_id, dept_id, dept_name)\n    dept_name depends on dept_id, not emp_id. Transitive: emp_id → dept_id → dept_name.\n  Fix: separate departments(dept_id, dept_name) table.\n\nBCNF (stricter 3NF): every determinant is a candidate key. Rarely needed in practice.\n\nWhen to DENORMALIZE:\n  - Analytics/OLAP: star schema (fact table + dimension tables) is intentionally flat for fast aggregation\n  - Read-heavy with rare updates: cache computed columns (total_items on orders table)\n  - Avoid N+1 query: store user.city on orders to avoid joining users on every order read\n  - Trade-off: update anomalies — if city changes, must update all orders too"
    },
    {
        "id": "sql_058",
        "difficulty": "Medium",
        "category": "CONCEPTS / QUERY",
        "is_conceptual": True,
        "title": "CTEs vs Subqueries vs Temp Tables",
        "description": "What's the difference between a CTE, a subquery, and a temp table? When does each perform better? Are CTEs materialized?",
        "key_concept": "Subqueries: inline, may re-execute. CTEs: named, readable, sometimes optimized as inline. Temp tables: physically stored, have indexes, best for large intermediate results used multiple times.",
        "hints": {
            "L1": "All three let you break a query into steps. What's the key difference when the intermediate result is large and used twice?",
            "L2": "Subquery: optimizer may execute it multiple times (in WHERE EXISTS, correlated). CTE: in most DBs (PostgreSQL <12, SQL Server) CTEs are NOT materialized — they inline like subqueries. PostgreSQL 12+ materializes CTEs with MATERIALIZED keyword. Temp tables: always materialized, can be indexed.",
            "L3": "Use temp table when: intermediate result is large AND used multiple times, or you need to add an index to the intermediate result for a subsequent join. Use CTE for readability. Use subquery for simple one-use expressions."
        },
        "optimal_solution": "Subquery:\n  SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE country = 'US');\n  - Inline, no separate storage\n  - Correlated subqueries run once PER ROW — can be slow\n  - Good for simple one-use filters\n\nCTE (Common Table Expression):\n  WITH us_customers AS (\n    SELECT id FROM customers WHERE country = 'US'\n  )\n  SELECT * FROM orders WHERE customer_id IN (SELECT id FROM us_customers);\n  - Named, readable, recursive (WITH RECURSIVE)\n  - In PostgreSQL <12 and SQL Server: optimizer may inline it (not materialized)\n  - PostgreSQL 12+: use MATERIALIZED to force storage: WITH x AS MATERIALIZED (...)\n  - Same performance as equivalent subquery in most cases\n\nTemp Table:\n  CREATE TEMP TABLE us_customers AS\n    SELECT id FROM customers WHERE country = 'US';\n  CREATE INDEX ON us_customers(id); -- add index!\n  SELECT * FROM orders WHERE customer_id IN (SELECT id FROM us_customers);\n  DROP TABLE us_customers;\n  - Physically stored (survives query boundary, visible to next queries in session)\n  - Can be indexed → fast for large intermediate result used multiple times\n  - Overhead: write to disk, explicit cleanup\n\nChoose temp table when intermediate result > 100K rows used in 2+ subsequent joins."
    },
    {
        "id": "sql_059",
        "difficulty": "Hard",
        "category": "CONCEPTS / QUERY",
        "is_conceptual": True,
        "title": "Reading an EXPLAIN Plan",
        "description": "What does EXPLAIN / EXPLAIN ANALYZE tell you in PostgreSQL? What are the key nodes to look for and what are common performance anti-patterns you'd spot in a query plan?",
        "key_concept": "EXPLAIN shows the optimizer's plan: scan type (seq scan vs index scan), join method (hash join vs nested loop), estimated vs actual rows, cost. Look for seq scans on large tables, nested loops on large sets, bad estimates.",
        "hints": {
            "L1": "EXPLAIN shows what the database PLANS to do. EXPLAIN ANALYZE actually executes and shows what it DID. What's the most important thing to look for when a query is slow?",
            "L2": "Key nodes: Seq Scan (full table scan — red flag on large table), Index Scan (uses index), Index Only Scan (covering index, fastest), Hash Join (builds hash table from smaller side), Nested Loop (for each row in outer, scan inner — good for small sets), Merge Join (both sides sorted). Look at 'rows' estimate vs actual — huge mismatch = stale statistics.",
            "L3": "Anti-patterns in plan: Seq Scan on a 10M row table, Nested Loop where outer side is 100K rows (= 100K index lookups), Filter: rows removed by filter 99.9% (index would help), Sort (may indicate missing index for ORDER BY). Fix stale stats: ANALYZE table_name."
        },
        "optimal_solution": "EXPLAIN ANALYZE SELECT o.id, c.name\nFROM orders o\nJOIN customers c ON c.id = o.customer_id\nWHERE o.status = 'pending'\nORDER BY o.created_at DESC\nLIMIT 20;\n\nKey plan nodes:\n  Seq Scan: reads every row. OK for small tables or when filtering < 5% of rows.\n  Index Scan: follows index B-tree, then fetches row. Good for selective filters.\n  Index Only Scan: all data in index — fastest, no table access.\n  Bitmap Heap Scan: batches multiple index entries, then fetches pages — for moderately selective filters.\n  Hash Join: builds hash table from smaller side, probes with larger side. Good for large unsorted tables.\n  Nested Loop: for each outer row, find matching inner rows. Good when inner side is small or indexed.\n  Merge Join: both sides sorted on join key. Good when already sorted or indexed.\n\nWhat to look for:\n  1. Seq Scan on large table → missing index?\n  2. rows=1 estimate but actual=100000 → stale statistics (run ANALYZE)\n  3. Nested Loop with large outer side → hash join might be better (work_mem)\n  4. Sort node → missing index for ORDER BY / missing composite index\n  5. Filter (rows removed) → index on that column?\n\nFix stale stats: ANALYZE orders;\nForce re-plan after schema change: VACUUM ANALYZE;"
    },
    {
        "id": "sql_060",
        "difficulty": "Hard",
        "category": "CONCEPTS / DESIGN",
        "is_conceptual": True,
        "title": "Table Partitioning — Range, Hash, and List",
        "description": "What is table partitioning? Explain range, hash, and list partitioning. What problems does it solve and what are the trade-offs?",
        "key_concept": "Partitioning splits a large table into physical sub-tables by a partition key. Benefits: partition pruning (only scan relevant partitions), easier archival, parallel scan. Trade-offs: joins across partitions, FK constraints limited.",
        "hints": {
            "L1": "Partitioning is a performance and manageability technique for large tables. How does it help when most queries filter on a date range?",
            "L2": "Range: partition by date ranges (2024-01, 2024-02...). Hash: distribute rows evenly by hash of a key — good for uniform access patterns. List: explicit value groupings (country IN ('US', 'CA')).",
            "L3": "Partition pruning: query planner eliminates irrelevant partitions. WHERE created_at > '2025-01-01' → only scans 2025+ partitions. Downside: queries that don't filter on the partition key scan all partitions — potentially slower than unpartitioned."
        },
        "optimal_solution": "Partitioning splits one logical table into multiple physical storage segments (partitions).\n\nRange Partitioning (most common):\n  CREATE TABLE orders (id BIGINT, created_at DATE, total NUMERIC)\n  PARTITION BY RANGE (created_at);\n\n  CREATE TABLE orders_2024 PARTITION OF orders\n    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');\n  CREATE TABLE orders_2025 PARTITION OF orders\n    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');\n\n  Query: WHERE created_at > '2025-01-01' → ONLY scans orders_2025 (partition pruning)\n\nHash Partitioning:\n  PARTITION BY HASH (customer_id);\n  -- Evenly distributes rows by customer_id hash — balances write load\n  -- Good when no natural range exists and access is uniform\n\nList Partitioning:\n  PARTITION BY LIST (region);\n  -- FOR VALUES IN ('US', 'CA') → one partition for North America\n  -- FOR VALUES IN ('UK', 'DE', 'FR') → one partition for Europe\n\nBenefits:\n  - Partition pruning: skip irrelevant partitions in queries\n  - DROP old partition = instant archival (vs DELETE millions of rows)\n  - Parallel query: different partitions scanned in parallel\n  - Smaller indexes per partition → faster maintenance\n\nTrade-offs:\n  - Queries without partition key filter = full scan across all partitions\n  - Global indexes not supported (PostgreSQL) — each partition has its own\n  - Cross-partition joins are expensive\n  - FK constraints complex"
    },
    {
        "id": "sql_061",
        "difficulty": "Hard",
        "category": "CONCEPTS / DESIGN",
        "is_conceptual": True,
        "title": "Sharding vs Partitioning",
        "description": "What is the difference between sharding and partitioning? What problems does sharding solve that partitioning doesn't? What are the challenges of a sharded database?",
        "key_concept": "Partitioning: splits data within ONE database server. Sharding: splits data across MULTIPLE servers. Sharding solves write throughput limits and dataset size beyond one machine. Trade-off: cross-shard queries, distributed transactions, rebalancing complexity.",
        "hints": {
            "L1": "Partitioning splits one table across multiple physical files on ONE server. Sharding puts different data on DIFFERENT servers. What limit does partitioning not solve that sharding does?",
            "L2": "Partitioning: stays within one DB — single write bottleneck, single machine memory/CPU limit. Sharding: each shard is its own DB server — horizontal scale. Shard key choice is critical: poor key = hot shard, cross-shard queries.",
            "L3": "Sharding challenges: (1) cross-shard JOINs are not native — must be done in application layer, (2) distributed transactions (2-phase commit or eventual consistency), (3) rebalancing when adding shards, (4) the shard key can't change after assignment."
        },
        "optimal_solution": "Partitioning:\n  - Splits a large table into sub-tables on the SAME database server\n  - Managed by the DB engine (PostgreSQL PARTITION BY, MySQL partitions)\n  - Solves: query performance (pruning), archival, index size\n  - Does NOT solve: single-machine CPU/RAM/write throughput limits\n\nSharding:\n  - Splits data across MULTIPLE database servers (nodes)\n  - Each shard is a fully independent DB instance\n  - Solves: horizontal scale — data/traffic beyond what one server handles\n  - Common approaches:\n      Range sharding: users 0-999999 → shard 1, 1000000-1999999 → shard 2\n      Hash sharding: shard = hash(user_id) % num_shards (uniform distribution)\n      Directory sharding: lookup table maps user_id → shard (flexible but lookup overhead)\n\nChallenges:\n  - Cross-shard queries: JOIN across shards requires app-level fan-out + merge\n  - Distributed transactions: 2-phase commit (slow) or accept eventual consistency\n  - Hot shards: poor key choice causes uneven load (all new users on 'latest' shard)\n  - Rebalancing: adding a shard requires moving data\n  - Schema changes: must deploy to all shards\n\nWho does it:\n  - Application-level: Vitess (YouTube/MySQL), Citus (PostgreSQL)\n  - Native: MongoDB (automatic sharding), Cassandra (consistent hashing)"
    },
    {
        "id": "sql_062",
        "difficulty": "Medium",
        "category": "CONCEPTS / QUERY",
        "is_conceptual": True,
        "title": "The N+1 Query Problem",
        "description": "What is the N+1 query problem? How do you identify it and what are the solutions?",
        "key_concept": "N+1: 1 query to fetch N records, then N individual queries to fetch related data. Total = N+1 queries instead of 1-2. Fix: eager loading (JOIN or IN clause), or batching.",
        "hints": {
            "L1": "You fetch 100 orders, then for each order you run a separate query to get the customer name. How many queries total?",
            "L2": "101 queries (1 + 100). ORM anti-pattern: `for order in orders: print(order.customer.name)` triggers a SELECT per iteration if customer is lazy-loaded.",
            "L3": "Solutions: (1) JOIN in the initial query, (2) use IN clause to batch-fetch all related records at once, (3) ORM eager loading (.includes(), .with(), .prefetch_related()), (4) DataLoader pattern (batches requests in GraphQL)."
        },
        "optimal_solution": "N+1 problem — fetching related data in a loop:\n\n-- N+1 (bad):\nSELECT * FROM orders;  -- 1 query, returns 100 rows\n-- then in application:\nFOR each order:\n    SELECT name FROM customers WHERE id = order.customer_id;  -- 100 queries!\n-- Total: 101 queries\n\n-- Fix 1: JOIN upfront\nSELECT o.*, c.name AS customer_name\nFROM orders o\nJOIN customers c ON c.id = o.customer_id;\n-- 1 query\n\n-- Fix 2: IN clause (when you can't JOIN easily)\nSELECT * FROM orders;  -- returns order.customer_ids: [1, 2, 3, ...]\nSELECT id, name FROM customers WHERE id IN (1, 2, 3, ...);  -- 1 batch query\n-- 2 queries total, merge in application\n\nHow to identify:\n  - Query count scales with result count\n  - ORM debug logging shows repeated similar queries\n  - APM tools (Datadog, New Relic) show high query count per request\n  - EXPLAIN: look for repeated identical queries with different parameter values\n\nORM eager loading examples:\n  Rails: Order.includes(:customer)  -- LEFT JOIN or separate IN query\n  Django: Order.objects.select_related('customer')\n  Sequelize: Order.findAll({ include: Customer })"
    },
    {
        "id": "sql_063",
        "difficulty": "Medium",
        "category": "CONCEPTS / DESIGN",
        "is_conceptual": True,
        "title": "OLTP vs OLAP",
        "description": "What is the difference between OLTP and OLAP workloads? How do their database designs differ, and why can't you use the same DB for both?",
        "key_concept": "OLTP: transactional, many short reads/writes, normalized. OLAP: analytical, few complex queries over many rows, denormalized (star schema). Mixing them causes contention — analytics hurt transactional performance.",
        "hints": {
            "L1": "OLTP = Online Transaction Processing. OLAP = Online Analytical Processing. A checkout flow is OLTP. A 'total revenue by region last quarter' report is OLAP. What's different about the query patterns?",
            "L2": "OLTP: high-concurrency, short queries (single row by PK), write-heavy, needs ACID, normalized schema. OLAP: low-concurrency, full table scans over millions of rows, read-only, aggregations, denormalized (star/snowflake schema).",
            "L3": "Solutions: separate OLAP system (data warehouse: Redshift, BigQuery, Snowflake), ETL/ELT pipeline to sync OLTP data to warehouse, or use read replicas + materialized views for moderate analytics."
        },
        "optimal_solution": "OLTP (Online Transaction Processing):\n  - Purpose: run the business (orders, payments, user accounts)\n  - Queries: point lookups by PK, short transactions (< 100ms)\n  - Write pattern: high concurrency, many small writes\n  - Schema: normalized (3NF) — minimize redundancy, easy updates\n  - DB: PostgreSQL, MySQL, SQL Server\n  - Example: INSERT INTO orders ..., UPDATE inventory SET qty = qty - 1\n\nOLAP (Online Analytical Processing):\n  - Purpose: analyze the business (revenue trends, funnel analysis, cohorts)\n  - Queries: full scans, GROUP BY on 100M rows, complex aggregations\n  - Write pattern: batch loads (nightly ETL/ELT)\n  - Schema: denormalized (star/snowflake schema) — optimize for reads, not writes\n  - DB: Redshift, BigQuery, Snowflake, ClickHouse\n  - Example: SELECT region, SUM(total) FROM orders WHERE year = 2025 GROUP BY region\n\nWhy not mix them:\n  Analytics queries scan millions of rows → lock contention, I/O saturation\n  Hurts transactional response time and SLAs\n\nSolution:\n  ETL/ELT pipeline: OLTP → (nightly sync) → Data Warehouse\n  Or: read replicas for moderate analytics\n  Or: materialized views refreshed periodically"
    },
    {
        "id": "sql_064",
        "difficulty": "Medium",
        "category": "CONCEPTS / DESIGN",
        "is_conceptual": True,
        "title": "Star Schema vs Snowflake Schema",
        "description": "What is a star schema? How does it differ from a snowflake schema? In what context are these used and why?",
        "key_concept": "Star schema: one central fact table + denormalized dimension tables (one join from fact). Snowflake: dimensions normalized into sub-dimensions (more joins). Star = simpler/faster queries. Snowflake = less storage, more normalized.",
        "hints": {
            "L1": "Star and snowflake schemas are data warehouse designs. The central table holds measures (revenue, quantity). What are the surrounding tables called, and what do they hold?",
            "L2": "Fact table: numeric metrics + foreign keys to dimensions (order_id, amount, date_id, customer_id, product_id). Dimension tables: descriptive attributes (customers: name, city, segment; dates: year, quarter, month). Star schema: dimensions are flat. Snowflake: dimensions have their own sub-dimensions (city → state → country tables).",
            "L3": "BI tools (Tableau, Looker) work best with star schemas — fewer joins = faster queries and simpler models. Snowflake reduces storage but requires more joins. Most data warehouses favor star schema for analytics performance."
        },
        "optimal_solution": "Data warehouse schemas — optimized for analytical queries.\n\nSTAR SCHEMA:\n  fact_orders: order_id, date_id, customer_id, product_id, amount, quantity\n       ↓             ↓            ↓             ↓\n  dim_dates    dim_customers  dim_products  (flat, denormalized)\n\n  dim_customers: customer_id, name, email, city, state, country, segment\n  (all customer attributes in ONE table — denormalized)\n\n  Advantages:\n    - Simple: always 1 join from fact to dimension\n    - Fast: fewer joins = better query performance\n    - BI-tool friendly: Tableau/Looker/Power BI model well\n\nSNOWFLAKE SCHEMA:\n  fact_orders → dim_customers → dim_cities → dim_states → dim_countries\n  (dimensions normalized into sub-dimensions)\n\n  Advantages:\n    - Less storage (no repeated country name per customer)\n    - More normalized — easier to update dimension values\n  Disadvantages:\n    - More joins in every analytical query\n    - More complex SQL\n    - Slower queries at scale\n\nPractice:\n  Most data warehouses use star schema (or slight variations).\n  Snowflake schema is used when dimension tables are very large and storage matters.\n  The goal of both: optimize for SELECT aggregation performance, not write performance."
    },
    {
        "id": "sql_065",
        "difficulty": "Medium",
        "category": "CONCEPTS / DESIGN",
        "is_conceptual": True,
        "title": "Stored Procedures vs Views vs Functions",
        "description": "What are stored procedures, user-defined functions (UDFs), and views? When would you use each, and what are the trade-offs of putting business logic in the database?",
        "key_concept": "View: named query, no parameters, read-only. Function: takes params, returns value, usable in SELECT. Stored procedure: parameterized, can have side effects (INSERT/UPDATE), returns sets or OUT params. Trade-off: logic in DB = harder to version/test.",
        "hints": {
            "L1": "Views are like named SELECT statements. Functions return a value and can be called in a SELECT. Stored procedures execute logic and can modify data. When would you choose a procedure over application code?",
            "L2": "Use stored procedures for: complex multi-step transactions that must be atomic, bulk operations (avoid network round-trips), when DBA-controlled logic is required. Downsides: hard to version control, can't unit test easily, DB becomes a logic layer.",
            "L3": "Modern trend: keep business logic in the application layer (easier to test, version, deploy). Use DB for: data integrity (constraints, triggers), performance-critical bulk operations. Views for abstraction. Functions for reusable SQL expressions."
        },
        "optimal_solution": "VIEW:\n  CREATE VIEW active_orders AS\n    SELECT id, customer_id, total FROM orders WHERE status != 'cancelled';\n  - No parameters, no logic, just a named query\n  - Readable in SELECT like a table\n  - Cannot modify data (usually)\n\nUSER-DEFINED FUNCTION (UDF):\n  CREATE FUNCTION get_customer_ltv(cid INT) RETURNS NUMERIC AS $$\n    SELECT COALESCE(SUM(total), 0) FROM orders WHERE customer_id = cid;\n  $$ LANGUAGE SQL;\n\n  -- Use in SELECT:\n  SELECT id, name, get_customer_ltv(id) AS ltv FROM customers;\n  - Takes parameters, returns a scalar or table\n  - Callable inline in queries\n  - Should be pure (no side effects) for optimizer to cache\n\nSTORED PROCEDURE:\n  CREATE PROCEDURE process_refund(order_id INT, amount NUMERIC)\n  LANGUAGE plpgsql AS $$\n  BEGIN\n    UPDATE orders SET refunded = TRUE WHERE id = order_id;\n    INSERT INTO refunds(order_id, amount, created_at) VALUES (order_id, amount, NOW());\n    PERFORM notify_customer(order_id);\n  END;\n  $$;\n\n  CALL process_refund(42, 29.99);\n  - Multi-step, can INSERT/UPDATE/DELETE\n  - Atomic when wrapped in transaction\n  - Can accept OUT parameters\n\nTrade-offs of DB logic:\n  Pro: reduced network round-trips, enforced at DB level, sometimes faster\n  Con: hard to version control (not in Git easily), hard to unit test, tightly coupled to DB\n  Modern advice: prefer application-layer logic; use DB for integrity and performance-critical bulk ops"
    },
]

for q in QUESTIONS:
    out = OUT / f"{q['id']}.json"
    out.write_text(json.dumps(q, indent=2) + "\n")

print(f"Written {len(QUESTIONS)} conceptual SQL questions ({QUESTIONS[0]['id']}–{QUESTIONS[-1]['id']}) to {OUT}")
