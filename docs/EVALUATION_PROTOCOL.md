# Evaluation Protocol

This project is a behavioral evaluation framework for synthetic scenarios.

It is useful for comparative analysis, regression tracking, and failure-mode discovery. It is not a deployment certification framework.

## 1. Valid Claims

You can claim:

- Relative differences between agents under the same scenario, variant, and seed policy.
- Directional behavior changes across `unconstrained`, `soft_guidelines`, and `hard_rules` variants.
- Regression or improvement versus a previously published baseline with reproducible artifacts.
- Observed failure patterns in hidden metrics and fairness disparity indicators.

## 2. Invalid Claims

Do not claim:

- Universal model quality rankings.
- Real-world safety certification or legal/compliance readiness.
- Causal claims from single-run outcomes.
- "Ground truth" conclusions without artifact-level evidence.

## 3. Required Metadata for Any Published Result

Every published result or leaderboard entry must include:

- repo commit SHA
- execution date in UTC
- simulation id
- duration and variant
- agent/model identifiers
- seed policy (fixed seed, explicit seed list, or random)
- run count per condition (`n`)
- artifact paths and manifest hash references
- scoring metric path(s) used for ranking or gating

## 4. Minimum Statistical Policy

Minimum policy for public comparative claims:

- `n >= 5` runs per condition
- identical seed list across compared conditions
- report mean, stddev, and 95% CI
- include raw run-level artifacts

If `n < 5`, mark claims as exploratory.

## 5. Fairness and Harm Reporting

When a simulation exposes fairness disparity metrics:

- report at least one disparity metric alongside the headline score
- avoid averaging away subgroup disparities
- call out tradeoffs where headline composite improves while disparity worsens

## 6. Anti-Gaming Rules

To keep results credible:

- lock prompts/scoring before comparative runs
- do not tune prompts using hidden metric internals
- document any scenario-specific adaptation strategy
- keep baselines versioned and changelog threshold changes
- publish failed runs and exclusions with reason codes

## 7. Reproducibility Workflow

Use this workflow for published claims:

```bash
python3 scripts/doctor.py --skip-agents
python3 scripts/seed_sweep.py --agents codex --simulation prisoners_dilemma --seeds 11,22,33,44,55 --variant hard_rules --duration 10 --results-dir results/seed_sweeps/ipd_hard
python3 scripts/summarize_results.py --results-file results/seed_sweeps/ipd_hard/seed_11.json --results-file results/seed_sweeps/ipd_hard/seed_22.json --results-file results/seed_sweeps/ipd_hard/seed_33.json --results-file results/seed_sweeps/ipd_hard/seed_44.json --results-file results/seed_sweeps/ipd_hard/seed_55.json --metric composite_score --group-by simulation,variant,agent_type,effective_model --output results/seed_sweeps/ipd_hard/summary.json --quiet
python3 scripts/regression_gate.py --summary-file results/seed_sweeps/ipd_hard/summary.json --baseline-file benchmarks/smoke_regression_baseline_v1.json
python3 scripts/results_coverage.py --output results/coverage/release_snapshot.json --quiet
```

## 8. Publication Standard

A release post is publication-ready only when:

- commands and artifacts are reproducible from a fresh clone
- claims match this protocol
- limitations are stated clearly
- source artifacts are linked
