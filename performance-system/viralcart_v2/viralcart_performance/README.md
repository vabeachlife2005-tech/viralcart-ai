# ViralCart AI Worker Performance Scoreboard
Created 2026-11-23. This is a baseline and measurement framework, not a claim of live integration.

## Baseline from connected Gmail and automation records
- Prospect outbound emails: 28 (Nov 23, connected account)
- Confirmed hard bounces: 1 (marketing@anker.com; suppress)
- Qualified human buying replies: 0 verified
- Paid orders / revenue: 0 verified / $0 verified
- Automated replies: present; do not count as qualified interest
- Growth/Foresight and AI Systems have earlier completed runs; other three have no completed runs recorded at baseline.

## Data dictionary
Every worker run adds a row to worker_runs.csv with timestamp, worker, deliverable, evidence, completion, quality, blockers, next action, and estimated/verified impact. Never backfill fake outcomes.

## Weekly scoring (0-100)
- Evidence-backed deliverable: 30
- Accuracy and QA: 25
- Revenue or cost relevance: 20
- Completion and timeliness: 15
- Clear next experiment and owner: 10
If no executed work, mark blocked and score only verified criteria. Scoring is a management heuristic, not an objective AI capability benchmark.

## Core sales funnel
verified prospects -> approved outreach -> delivered -> human reply -> qualified conversation -> paid trial -> accepted delivery -> repeat buyer.
Keep auto-replies, bounces, and opt-outs separate. No conversion rate without denominator.

## 25 operational patterns
See patterns.csv for owners, proposed application, and acceptance test. These are original operational rules inspired by public best practices, not copied proprietary commands or automatically installed software.
