# Testing Guide

This repo uses contract tests, CLI regression tests, and targeted runner tests.

## Quick Validation (Required Before PR)

```bash
python3 -m py_compile $(rg --files -g '*.py')
python3 run_race.py --help
python3 run_benchmark.py --help
bash -n run_benchmark.sh
pytest -q tests/test_scenario_registry.py tests/test_race_prompts.py tests/test_new_scenario_script.py
pytest -q tests/test_race_config.py tests/test_race_preflight.py tests/test_race_scenario_io.py
```

## Full CLI Regression Suite

```bash
pytest -q tests/test_*_cli.py
```

## Targeted Runner Tests

```bash
pytest -q tests/test_run_race_results.py tests/test_run_race_schema.py
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
