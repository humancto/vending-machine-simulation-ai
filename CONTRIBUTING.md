# Contributing to The Simulation Crucible

This project is an open behavioral stress-test suite for AI agents.

It is intentionally **not** positioned as an "ultimate benchmark" or a universal ranking oracle. Contributions should improve reproducibility, scenario quality, and methodological transparency.

## Add a New Simulation (Fast Path)

Use the scaffold script:

```bash
python3 scripts/new_scenario.py \
  --id grid_failure \
  --code gf \
  --cli-code gf \
  --title "Grid Failure Response" \
  --duration-arg days
```

This generates:

- `prompts/<id>/unconstrained.md`
- `prompts/<id>/soft_guidelines.md`
- `prompts/<id>/hard_rules.md`
- `simulations/<id>/__init__.py`
- `simulations/<id>/simulation.py`
- `sim_cli/<cli-code>_cli.py`
- `tests/test_<cli-code>_cli.py`
- Appends a registry entry in `race/scenario_registry.py` (unless `--no-registry`).

## PR Checklist for New Simulations

1. Implement simulation logic in `simulations/<id>/simulation.py`.
2. Implement CLI behavior in `sim_cli/<code>_cli.py`.
3. Replace scaffold test with real tests in `tests/test_<code>_cli.py`.
4. Ensure prompts for all three variants are present and coherent.
5. Confirm `race/scenario_registry.py` entry is correct:
   - `simulation_id`
   - display label
   - prompt code
   - duration arg/label/default
6. Add or update scenario docs in `README.md` if user-facing.

## Validation Before Opening a PR

Run at minimum:

```bash
python3 -m py_compile $(rg --files -g '*.py')
python3 run_race.py --help
pytest -q tests/test_*_cli.py
```

If you touched simulation internals, run related unit/integration tests too.

## Design Principles

- Keep scenario behavior deterministic under the same seed.
- Prefer explicit hidden-metric accounting over implicit side effects.
- Keep CLI contracts stable (`start`, `status`, `advance`, `full-score` style).
- Avoid benchmark hype in docs; be clear about limitations and scope.
