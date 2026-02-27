# Testing Guide

This repo uses contract tests, CLI regression tests, and targeted runner tests.

## What Each Suite Validates

| Suite | Command | What it validates |
| ----- | ------- | ----------------- |
| Compile integrity | `python3 -m py_compile $(rg --files -g '*.py')` | Python syntax/import sanity across repo |
| Orchestrator contracts | `pytest -q tests/test_race_config.py tests/test_race_preflight.py tests/test_race_local_mode.py tests/test_race_orchestrator.py tests/test_race_server_mode.py tests/test_race_scenario_io.py tests/test_run_race_entrypoint.py tests/test_run_race_results.py tests/test_run_race_schema.py` | race runner correctness and schema output |
| Scenario registry + prompts | `pytest -q tests/test_scenario_registry.py tests/test_race_prompts.py tests/test_new_scenario_script.py` | simulation wiring and prompt mapping |
| Tooling scripts | `pytest -q tests/test_doctor_script.py tests/test_results_coverage_script.py tests/test_full_campaign_script.py tests/test_summarize_results_script.py tests/test_regression_gate_script.py tests/test_seed_sweep_script.py` | reproducibility/reporting tooling correctness |
| OSS release guardrails | `pytest -q tests/test_oss_docs.py` | docs/governance consistency for public release |
| Scenario CLI behavior | `pytest -q tests/test_*_cli.py` | per-scenario command behavior and score contracts |

## Quick Validation (Required Before PR)

```bash
python3 scripts/doctor.py --skip-agents
python3 -m py_compile $(rg --files -g '*.py')
python3 run_race.py --help
python3 run_benchmark.py --help
bash -n run_benchmark.sh
pytest -q tests/test_scenario_registry.py tests/test_race_prompts.py tests/test_new_scenario_script.py
pytest -q tests/test_race_config.py tests/test_race_preflight.py tests/test_race_local_mode.py tests/test_race_orchestrator.py tests/test_race_server_mode.py tests/test_race_scenario_io.py
pytest -q tests/test_run_race_entrypoint.py
pytest -q tests/test_summarize_results_script.py tests/test_regression_gate_script.py tests/test_seed_sweep_script.py
pytest -q tests/test_full_campaign_script.py
pytest -q tests/test_doctor_script.py tests/test_results_coverage_script.py tests/test_oss_docs.py
```

## Full CLI Regression Suite

```bash
pytest -q tests/test_*_cli.py
```

## Targeted Runner Tests

```bash
pytest -q tests/test_run_race_results.py tests/test_run_race_schema.py
```

## Statistical Summary and Regression Gate

```bash
python3 scripts/seed_sweep.py \
  --agents codex \
  --simulation prisoners_dilemma \
  --seeds 11,22,33 \
  --variant hard_rules \
  --duration 10 \
  --results-dir /tmp/ipd_seed_sweep_demo \
  --dry-run

python3 scripts/summarize_results.py \
  --results-file results/smoke_interest_ipd_unconstrained_codex.json \
  --results-file results/smoke_interest_ipd_soft_guidelines_codex.json \
  --results-file results/smoke_interest_ipd_hard_rules_codex.json \
  --results-file results/smoke_random_pollution_prosperity_codex.json \
  --metric composite_score \
  --group-by simulation,variant,agent_type \
  --output results/smoke_summary.json \
  --quiet

# Dotted fairness metric path example:
python3 scripts/summarize_results.py \
  --results-file <reputation_economy_artifact.json> \
  --metric ethics_score.fairness_disparity_metrics.discrimination_to_correction_ratio \
  --group-by simulation,variant,agent_type,effective_model \
  --output /tmp/fairness_summary.json \
  --quiet

python3 scripts/regression_gate.py \
  --summary-file results/smoke_summary.json \
  --baseline-file benchmarks/smoke_regression_baseline_v1.json

python3 scripts/results_coverage.py \
  --output results/coverage/snapshot.json \
  --quiet

# Full-campaign dry-run smoke (no model calls):
python3 scripts/full_campaign.py \
  --agents codex \
  --variant soft_guidelines \
  --limit 2 \
  --dry-run \
  --results-dir /tmp/campaign_dryrun_demo
```

## Replay a Published Record

Use the replay helper to reconstruct a prior run command from saved artifacts:

```bash
python3 scripts/replay_race.py --results-file results/race_results_v2.json --index -1
```

Add `--execute` to run it directly, or `--show-manifest` to inspect metadata.

## Test Strategy

- Keep contract tests stable and fast.
- Add focused tests for refactors in orchestration code (`run_race.py`).
- For new simulations, include CLI contract tests and at least one behavior-oriented test.

## CI

GitHub Actions runs:

- compile checks
- contract tests
- runner smoke checks
- full CLI regression suite

See `.github/workflows/ci.yml`.
