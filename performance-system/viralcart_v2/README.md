# ViralCart Worker Performance System v2

This upgrade preserves the uploaded original in `viralcart_performance/`, and adds a **working, dependency-free Python event ledger, validator, scoring engine, report generator, tests and GitHub Actions test workflow**. No external integrations or live services are claimed.

## Quick start

```bash
python -m unittest discover -s tests -v
python src/viralcart.py validate
python src/viralcart.py report
# copy data/sample_event.json to your own unique file, replace example values, then:
python src/viralcart.py record /path/to/event.json
python src/viralcart.py report
```

The original baseline is retained as a historical **snapshot**, not imported as 28 individual verified message events. That avoids manufacturing event-level evidence. New events require a unique event ID, timestamp, source, evidence and explicit status. Verified sends require approval reference. Estimated or hypothetical amounts never enter verified revenue. Rates without denominators are `null`.

## Data contracts

Event kinds: `lead`, `outreach_approved`, `email_sent`, `email_bounced`, `email_optout`, `reply_auto`, `reply_human`, `conversation_qualified`, `order_paid`, `creative_accepted`, `repeat_order`, `worker_run`, `experiment`.

`worker_run` requires worker (`lead`, `creative`, `systems`, `website`, `growth`), deliverable, owner and next_action. A complete verified rubric optionally yields a score out of 100: evidence 30, accuracy 25, impact 20, completion 15, next experiment 10. Unverified runs remain unscored. Score reflects evidence quality, not intelligence.

## Integration boundaries

Five existing ChatGPT scheduled workers have been instructed to output these structured fields. **The scheduled tasks do not automatically execute this Python project or persist records to its local data folder.** To achieve full integration, connect a persistent shared repo/storage and an authorized ingestion workflow. Avoid putting Gmail credentials or provider API keys in repository files. A future importer should use Gmail/automation APIs with explicit access, pagination, idempotency, and minimal data retention. Keep `data/events.jsonl` out of public repos if it contains personal/contact data.

## Release gate

Before enabling any real email sending, purchases, or deployment, implement identity, explicit approval verification, opt-out enforcement and server-side authorization. The `approval_ref` field is an audit requirement, **not** a security authorization mechanism.

## Deployment integration (v2.1)

- `src/import_events.py` accepts a JSONL export of worker events, checks all events before writing, skips repeated event IDs, and regenerates reports. Run `python src/import_events.py export.jsonl --dry-run` before importing.
- `.github/workflows/performance-report.yml` runs tests and creates a downloadable report artifact on manual dispatch or relevant repository changes. **It does not automatically ingest ChatGPT scheduled-worker results.**
- Never commit customer contact information, private Gmail content, or tokens. A separate authenticated worker-result export mechanism and private storage are needed for continuous synchronization.
- To deploy, copy the contents of this folder into a dedicated private repository or a `/performance` subdirectory with appropriately adjusted workflow paths. Confirm repository permissions before pushing.
