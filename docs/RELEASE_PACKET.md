# Release Packet (2026-02-27)

This file captures current release readiness and benchmark artifact status.

## 1. Release Position

Current recommendation:

- **Framework/OSS release**: ready now
- **Benchmark-results release**: ready for `soft_guidelines` codex all-simulation batch
- **`hard_rules` codex all-simulation batch**: in progress (explicit TODO track)

## 2. Completed This Cycle

- Production clone-and-run readiness (`scripts/doctor.py`).
- Evaluation governance docs:
  - `docs/EVALUATION_PROTOCOL.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/CONTRIBUTOR_TASK_BOARD.md`
  - `docs/LAUNCH_POST_TEMPLATES.md`
- Results coverage tooling (`scripts/results_coverage.py`).
- Full campaign runner (`scripts/full_campaign.py`) with resumable progress + postprocess.

## 3. Campaign Status Snapshot

### Soft Guidelines (Codex, seed 42)

Directory:

- `results/campaigns/all_sims_soft_codex_20260224-180134/`

Status:

- runs total: `50`
- runs ok: `50`
- runs failed: `0`
- coverage: `50/50` (`coverage_ratio = 1.0`)

Key artifacts:

- `progress.json`
- `summary.json`
- `coverage.json`
- `summary_auto.json` (covers all 50 scenarios)
- `summary_composite.json` (49 scenarios; `vending_machine` has no `composite_score` metric)
- `quality_report.json`
- `warning_scan.txt`

### Hard Rules (Codex, seed 42)

Directory:

- `results/campaigns/all_sims_hard_codex_20260227-163429/`

Status:

- in progress
- tracked as TODO for complete variant parity before stronger comparative claims

## 4. Minimum Public Claim Boundary

Safe claims now:

- The project is an open behavioral experiment framework with reproducible artifacts.
- A complete `soft_guidelines` codex all-simulation batch exists with published artifacts.
- This is useful for comparative behavior analysis and due diligence, not certification.

Avoid claiming now:

- universal benchmark authority
- deployment safety certification
- final cross-variant conclusions before `hard_rules` batch completion

## 5. Repro Commands

```bash
python3 scripts/doctor.py --skip-agents
python3 scripts/full_campaign.py --agents codex --variant soft_guidelines --skip-missing --continue-on-failure
python3 scripts/results_coverage.py --results-glob "results/campaigns/all_sims_soft_codex_20260224-180134/*.json" --output results/campaigns/all_sims_soft_codex_20260224-180134/coverage.json --quiet
```

## 6. Copy-Ready Short Announcement

```text
Open-sourcing: The Simulation Crucible

Simulation Crucible is an open behavioral experiment platform for AI agents.
It stress-tests model behavior in synthetic scenarios with hidden metrics, ethical pressure, and constraint variants.

Release snapshot:
- 50-scenario framework with reproducible runner flow
- complete codex soft_guidelines batch across all 50 scenarios (artifacts published)
- hard_rules full batch is in progress and tracked as TODO

Not an ultimate benchmark. Not deployment safety certification.

Repo: https://github.com/humancto/simulation-crucible
Protocol: docs/EVALUATION_PROTOCOL.md
Contribute: docs/CONTRIBUTOR_TASK_BOARD.md
```

## 7. Fast Publish Guide

If you want the shortest defensible launch path, use:

- `docs/RELEASE_READY_NOW.md`

## 8. Why This Release Is Useful

- Gives teams a reproducible behavioral test harness they can run locally.
- Ships a complete 50-scenario codex `soft_guidelines` artifact set, not just selective screenshots.
- Provides an open contribution path for scenario design and evaluation-method upgrades.
