# Release Packet (2026-02-24)

This file captures the current public-release state of the repository.

## 1. What Is Ready

- Clone-and-run core flow documented and validated (`scripts/doctor.py`).
- Evaluation claim boundaries published (`docs/EVALUATION_PROTOCOL.md`).
- Release and OSS checklist published (`docs/RELEASE_CHECKLIST.md`).
- Contributor entry path published (`docs/CONTRIBUTOR_TASK_BOARD.md`).
- Copy-ready launch posts published (`docs/LAUNCH_POST_TEMPLATES.md`).

## 2. Validation Snapshot

Executed and passed in this release pass:

- `python3 -m py_compile $(rg --files -g '*.py')`
- `pytest -q tests/test_oss_docs.py tests/test_doctor_script.py tests/test_results_coverage_script.py tests/test_summarize_results_script.py tests/test_regression_gate_script.py tests/test_seed_sweep_script.py tests/test_run_race_results.py tests/test_run_race_schema.py`
- Race smoke run:
  - `python3 run_race.py --simulation prisoners_dilemma --agents claude,codex --seed 42 --rounds 1 --variant soft_guidelines --max-turns 30 --skip-missing --results-file /tmp/release_smoke_results.json`

## 3. Artifact Coverage Snapshot

Generated with:

```bash
python3 scripts/results_coverage.py --output /tmp/release_results_coverage.json --quiet
```

Current snapshot:

- simulations with published artifacts: `4/50`
- coverage ratio: `0.08`

Interpretation:

- Framework release quality: ready.
- Benchmark-completeness quality: partial, still in-progress.

## 4. Public Claim Boundary

Safe public claim:

- "Simulation Crucible is an open behavioral experiment platform for comparative AI behavior analysis with reproducible artifacts and explicit limitations."

Avoid claiming:

- universal benchmark status
- deployment-safety certification
- complete scenario-bank benchmark coverage

## 5. Copy-Ready Announcement

```text
Open-sourcing: The Simulation Crucible

Simulation Crucible is an open behavioral experiment platform for AI agents.
It tests model behavior under synthetic scenarios with hidden metrics, ethical pressure, and constraint variants.

What is live now:
- 50-scenario framework architecture
- reproducible race runner and artifact manifests
- explicit evaluation protocol + release checklist
- contributor task board for scoped PRs

What this is not:
- not a universal benchmark
- not deployment safety certification

Repo: https://github.com/humancto/simulation-crucible
Protocol: docs/EVALUATION_PROTOCOL.md
Contribute: docs/CONTRIBUTOR_TASK_BOARD.md

If you run model evals and want to pressure-test behavior tradeoffs, feedback and PRs are welcome.
```
