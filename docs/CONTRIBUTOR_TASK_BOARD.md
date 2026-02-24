# Contributor Task Board

This board maps the credibility workstreams into clear PR-ready tasks.

## How to Pick a Task

1. Pick one task from a workstream below.
2. Open an issue using the matching template block.
3. Submit one focused PR with tests and docs updates.

## Labels

Use these labels on issues/PRs:

- `good first issue`
- `workstream-a` through `workstream-f`
- `docs`
- `testing`
- `fairness`
- `baseline`

## Workstream A: Statistical Reliability

### A-01 Add median/IQR and optional bootstrap CI

- Goal: Extend `scripts/summarize_results.py` with robust stats beyond mean/std/ci95.
- Done when: JSON schema includes median and iqr, tests cover deterministic fixtures.
- Labels: `workstream-a`, `testing`

Issue template text:

```text
Title: [A-01] Add median/IQR + bootstrap CI to summary script
Scope:
- Extend summary output with median and IQR
- Add optional bootstrap CI flag
- Keep existing fields backward compatible
Validation:
- pytest -q tests/test_summarize_results_script.py
```

### A-02 Per-seed trace CSV export

- Goal: Add `--trace-csv` output for external analysis.
- Done when: CSV contains one row per run record with group metadata and metric value.
- Labels: `workstream-a`, `good first issue`

## Workstream B: Regression Gating

### B-01 Scenario-level baseline packs

- Goal: Add `benchmarks/baselines/<scenario>.json` for top scenarios.
- Done when: each pack has schema validation + tests.
- Labels: `workstream-b`, `baseline`

### B-02 Baseline threshold changelog

- Goal: Add versioned changelog for threshold edits.
- Done when: threshold moves reference prior value, reason, and date.
- Labels: `workstream-b`, `docs`

## Workstream C: Fairness and Harm Metrics

### C-01 Add fairness regression thresholds

- Goal: Gate on fairness disparity metrics for configured scenarios.
- Done when: baseline rules include dotted fairness paths and tests cover pass/fail.
- Labels: `workstream-c`, `fairness`

### C-02 Expand fairness metrics to more scenarios

- Goal: add at least one disparity/integrity metric to additional high-impact scenarios.
- Done when: metric appears in `full-score` output and tests verify presence.
- Labels: `workstream-c`

## Workstream D: Baseline Agents

### D-01 Deterministic policy agents

- Goal: add `greedy`, `balanced`, `ethics_first` baselines through same CLI path.
- Done when: each baseline can race with reproducible output and tests pass.
- Labels: `workstream-d`

### D-02 Delta reporting versus policy baselines

- Goal: report model score deltas relative to policy agents.
- Done when: race summary includes explicit `delta_vs_*` fields.
- Labels: `workstream-d`, `testing`

## Workstream E: Reporting and Governance

### E-01 Release report manifest standard

- Goal: enforce a minimal report manifest block in published artifacts.
- Done when: docs and tests verify required fields.
- Labels: `workstream-e`, `docs`

### E-02 Release post checklist enforcement

- Goal: update PR template with result-release checks.
- Done when: PR template has explicit checklist items for claims and artifact links.
- Labels: `workstream-e`, `good first issue`

## Workstream F: Contribution Path

### F-01 New simulation done criteria enforcement

- Goal: require prompt variants, registry entry, tests, and fairness/integrity check for new simulations.
- Done when: `CONTRIBUTING.md` and tests enforce criteria.
- Labels: `workstream-f`

### F-02 Simulation starter example PR

- Goal: publish one small sample PR that demonstrates scaffold-to-finished simulation flow.
- Done when: contributors can copy the path with minimal ambiguity.
- Labels: `workstream-f`, `docs`

## Submission Standard

Every PR tied to this board should include:

- command output for validation
- tests for behavior changes
- docs updates for claim or workflow changes
- bounded scope (single workstream task preferred)
