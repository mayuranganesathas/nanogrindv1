# Nanobot Memory

## User
- Name: Mayu | Timezone: America/Los_Angeles (UTC−7 Mar–Oct, UTC−8 Nov–Feb)
- Preferred languages: JS/TS (algo, SQL), Python (AI/ML)
- Rest day: Sunday
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

## Schedule start date
2026-03-08 (Week 1 Day 1)
