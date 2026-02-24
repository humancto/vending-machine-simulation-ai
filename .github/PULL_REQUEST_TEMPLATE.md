## Summary

Describe the change and why it is needed.

## Type of Change

- [ ] Bug fix
- [ ] New simulation
- [ ] Refactor
- [ ] Documentation
- [ ] Test-only change

## Validation

- [ ] `python3 -m py_compile $(rg --files -g '*.py')`
- [ ] `python3 scripts/doctor.py --skip-agents`
- [ ] `python3 run_race.py --help`
- [ ] `python3 run_benchmark.py --help`
- [ ] `bash -n run_benchmark.sh`
- [ ] `pytest -q tests/test_scenario_registry.py tests/test_race_prompts.py tests/test_new_scenario_script.py`
- [ ] `pytest -q tests/test_oss_docs.py tests/test_doctor_script.py tests/test_results_coverage_script.py`
- [ ] `pytest -q tests/test_*_cli.py` (if CLI/simulation behavior changed)

## Documentation

- [ ] Updated README/docs where behavior or claims changed
- [ ] Updated screenshots (if UI changed)
- [ ] Added/updated tests for new behavior

## Checklist

- [ ] No secrets added
- [ ] Backward compatibility considered
- [ ] Scope is focused and reviewable
