# Credibility Execution Plan

This plan is for contributors who want to make Simulation Crucible more trustworthy, reproducible, and useful for due diligence.

## Goal

Ship a practical "credibility pack" without over-claiming:

- Reproducible runs
- Statistical summaries (not single-run hype)
- Explicit regression gates
- Clear documentation of what claims are valid

## Current Status (Batch 7.0a)

- [x] Multi-run summary tool with mean/std/95% CI: `scripts/summarize_results.py`
- [x] Threshold-based regression gate: `scripts/regression_gate.py`
- [x] Example baseline file: `benchmarks/smoke_regression_baseline_v1.json`
- [x] Script tests:
  - `tests/test_summarize_results_script.py`
  - `tests/test_regression_gate_script.py`

## Workstream A: Statistical Reliability

### A1. Seed Sweep Runner
- [x] Add `scripts/seed_sweep.py` to run `run_race.py` across seed lists.
- [x] Support scenario, variant, duration, agent list, and output directory.
- [x] Emit one artifact per run plus merged index JSON (seed sweep manifest).

### A2. Confidence Reporting
- [x] Aggregate mean/std/95% CI by group.
- [ ] Add median/IQR and bootstrap CI option.
- [ ] Add per-seed trace CSV export for external analysis.

### A3. Claim Guardrails
- [ ] Add `min_n` claim warnings in summary output.
- [ ] Flag unstable groups where CI is large relative to mean.

## Workstream B: Regression Gating

### B1. Baseline Policy
- [x] Baseline rule schema (`regression_gate_v1`) and checker.
- [ ] Add scenario-level baseline packs (`benchmarks/baselines/*.json`) for key scenarios.
- [ ] Add versioned changelog when baseline thresholds move.

### B2. CI Integration
- [x] Add contract test coverage for summary+gate integration on committed smoke artifacts.
- [ ] Add optional CI job to run gate on committed fixture artifacts.
- [ ] Document expected non-determinism policy (when not to gate).

## Workstream C: Fairness and Harm Metrics

### C1. Cross-Group Disparity Metrics
- [ ] For relevant sims (e.g., pollution, reputation, school), add disparity summaries:
  - max-min burden gap
  - ratio metrics for vulnerable vs non-vulnerable groups
- [ ] Expose in `full-score` JSON and results artifacts.

### C2. Fairness Regression Rules
- [ ] Allow `scripts/regression_gate.py` to gate on fairness sub-metrics using dotted paths.
- [ ] Add baseline thresholds specifically for fairness dimensions.

## Workstream D: Baseline Agents

### D1. Policy Bots
- [ ] Implement deterministic baseline agents:
  - `greedy`
  - `balanced`
  - `ethics_first`
- [ ] Ensure each baseline can run through the same CLI path as model agents.

### D2. Contextualized Leaderboards
- [ ] Show model score deltas against baseline bots, not just absolute rank.

## Workstream E: Reporting and Governance

### E1. Evaluation Protocol
- [ ] Publish `docs/EVALUATION_PROTOCOL.md`:
  - valid claims
  - invalid claims
  - required metadata
  - anti-gaming policy

### E2. Artifact Standards
- [ ] Require manifest block + seed policy in published reports.
- [ ] Add release checklist for benchmark result posts.

## Workstream F: Contribution Path

### F1. Easy PR Onboarding
- [ ] Add `docs/CONTRIBUTOR_TASK_BOARD.md` with "good first issue" labels mapped to workstreams.
- [ ] Add ready-to-copy issue templates for each workstream.

### F2. Done Criteria for Any New Simulation
- [ ] Require:
  - scenario registry entry
  - prompt variants
  - CLI tests
  - score schema fields
  - at least one fairness or integrity check

## Suggested Execution Order

1. A1 (seed sweep runner)
2. B2 (CI gate wiring for fixture artifacts)
3. C1 (fairness disparity metrics in 2-3 high-impact sims)
4. D1 (policy bots)
5. E1 (formal protocol doc)

## PR Checklist for This Plan

For changes touching evaluation claims or scoring:

- [ ] Include tests
- [ ] Update relevant docs
- [ ] Add/refresh baseline thresholds if needed
- [ ] Run `scripts/summarize_results.py` on updated artifacts
- [ ] Run `scripts/regression_gate.py` before merge
