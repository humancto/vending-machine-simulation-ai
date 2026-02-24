# Release Checklist

Use this checklist before announcing new benchmark findings or framework updates.

## 1. Scope Lock

- [ ] Define release type: framework release, result release, or both.
- [ ] Freeze claims and ensure they match `docs/EVALUATION_PROTOCOL.md`.
- [ ] Confirm no "ultimate benchmark" language appears in release text.

## 2. Fresh Clone Runability

- [ ] From a fresh clone, create venv and install dependencies.
- [ ] Run `python3 scripts/doctor.py --skip-agents`.
- [ ] Run `python3 run_race.py --help` and `python3 run_benchmark.py --help`.
- [ ] Boot `python3 server.py` and confirm local dashboard loads.

## 3. Validation

Run and pass:

```bash
python3 -m py_compile $(rg --files -g '*.py')
pytest -q tests/test_oss_docs.py tests/test_doctor_script.py tests/test_results_coverage_script.py
pytest -q tests/test_summarize_results_script.py tests/test_regression_gate_script.py tests/test_seed_sweep_script.py
pytest -q tests/test_run_race_results.py tests/test_run_race_schema.py
```

## 4. Result Integrity

- [ ] Generate/refresh summary artifacts with `scripts/summarize_results.py`.
- [ ] Run regression checks with `scripts/regression_gate.py`.
- [ ] Generate coverage report with `scripts/results_coverage.py`.
- [ ] Record missing simulations if coverage is partial.

## 5. Documentation

- [ ] `README.md` links are current.
- [ ] `docs/index.html` footer links are current.
- [ ] `docs/WHAT_THIS_TESTS.md` and `docs/EVALUATION_PROTOCOL.md` align.
- [ ] `docs/LAUNCH_POST_TEMPLATES.md` is up to date with current numbers.

## 6. OSS Hygiene

- [ ] `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, and `CONTRIBUTING.md` exist and are current.
- [ ] Issue templates and PR template match current workflow.
- [ ] No strategy or private planning docs are included in tracked files.

## 7. Git Release Hygiene

- [ ] `git status` clean.
- [ ] Commits are atomic and message history is readable.
- [ ] Branch is pushed.
- [ ] Tag or release draft prepared (if applicable).

## 8. Publish Pack

Publish with:

- summary of what changed
- explicit scope and limitations
- reproduction command block
- links to artifacts and baseline references
- one copy-ready public post from `docs/LAUNCH_POST_TEMPLATES.md`
