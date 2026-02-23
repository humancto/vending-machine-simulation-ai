# Runner Extension Points

This repo now uses a layered race-runner architecture:

- `run_race.py`: thin entrypoint + compatibility wrappers.
- `race/orchestrator.py`: top-level dispatch and mode routing.
- `race/local_mode.py`: no-server scenario execution path.
- `race/server_mode.py`: vending-machine server-backed execution path.
- `race/scenario_io.py`: scenario IO compatibility layer + vending/IPD helpers.
- `race/scenario_io_scenarios.py`: extracted local-scenario prompt/score helpers.
- `race/scenario_registry.py`: canonical scenario metadata (`prompt_code`, `cli_code`, `duration_arg`).

## Add a New Local Scenario

1. Add a `ScenarioSpec` entry in `race/scenario_registry.py` with:
   - `simulation_id`
   - `prompt_code`
   - `cli_code`
   - `duration_arg` / `duration_label` / `default_duration`
2. Add prompt variants under `prompts/<simulation_id>/`:
   - `unconstrained.md`
   - `soft_guidelines.md`
   - `hard_rules.md`
3. Implement two helpers in `race/scenario_io_scenarios.py` (exported via `race/scenario_io.py`):
   - `build_<prompt_code>_prompt(...)`
   - `collect_<prompt_code>_score(...)`
4. Add scenario CLI/test files (`sim_cli/`, `tests/test_<cli_code>_cli.py`).

No `run_race.py` branch should be needed for a normal local-mode scenario.

## Modify Runner Behavior Safely

- Dispatch logic: update `race/orchestrator.py`.
- Shared local execution behavior: update `race/local_mode.py`.
- Shared vending/server behavior: update `race/server_mode.py`.
- Keep `run_race.py` backward-compatible for:
  - `build_race_record(...)`
  - `append_race_record(...)`
  - `detect_model(...)`
  - `get_git_commit_sha(...)`

## Validation Checklist

Run before opening a PR:

```bash
python3 -m py_compile $(rg --files -g '*.py')
pytest -q tests/test_race_orchestrator.py tests/test_race_local_mode.py tests/test_race_server_mode.py tests/test_race_scenario_io.py
pytest -q tests/test_*_cli.py
```
