# Open Source Standards Tasks

Date: 2026-02-23
Goal: Raise the project to a high-trust, contributor-friendly OSS baseline.

## Batch 1: Governance and Community (Completed)

- [x] Add `LICENSE` (MIT).
- [x] Add `CODE_OF_CONDUCT.md`.
- [x] Add `SECURITY.md`.
- [x] Add `SUPPORT.md`.
- [x] Add PR template and issue templates.

## Batch 2: Methodology and Contributor Docs (Completed)

- [x] Add `docs/WHAT_THIS_TESTS.md` with explicit claims and limits.
- [x] Add `docs/TESTING.md` with local and CI commands.
- [x] Add `docs/SCREENSHOTS.md` with documentation asset standards.
- [x] Link these docs from `README.md`.
- [x] Add project copy updates to avoid "ultimate benchmark" positioning.

## Batch 3: Correctness and Drift Reduction (Completed)

- [x] Add runner persistence tests in `tests/test_run_race_results.py`.
- [x] Fix result persistence helper to create missing output directories.
- [x] Remove stale simulation-count drift in docs/marketing copy.

## Batch 4: Next Priority (Recommended)

- [x] Add run manifest schema (`commit_sha`, prompt hash, model id, seed policy).
- [x] Add schema validation tests for result artifacts.
- [x] Add a reproducibility command to replay published runs.
- [x] Add a docs consistency CI check (live simulation list vs registry).

## Batch 5: Next Priority (Recommended)

- [x] Refactor race record construction into a shared helper to remove branch duplication in `run_race.py`.
- [x] Emit explicit model override metadata per agent (not only detected defaults).
- [x] Add JSON schema file for race result records and validate in CI.
- [x] Add replay smoke test using a real generated artifact from a tiny fixture run.

## Local-Only Notes Policy

- Internal launch strategy artifacts are kept outside the public repo as local references.

## Batch 5.3: Config Extraction (Completed)

- [x] Extract CLI argument parsing and config prep into `race/config.py`.
- [x] Replace inline simulation flag wiring with shared `sim_flags` mapping.
- [x] Add config parser tests in `tests/test_race_config.py`.

## Batch 5.4: Preflight Extraction (Completed)

- [x] Extract agent availability/auth/model preflight helpers into `race/preflight.py`.
- [x] Keep compatibility wrappers in `run_race.py` to preserve existing monkeypatch/test seams.
- [x] Replace inline final-agent filtering with a shared helper in `race/preflight.py`.
- [x] Add preflight helper tests in `tests/test_race_preflight.py`.

## Batch 5.5: Prompt Fallback Cleanup (Completed)

- [x] Remove legacy prompt fallback branches from `race/prompts.py`.
- [x] Keep `run_race.py` prompt call sites compatible while enforcing scenario-based prompt files.
- [x] Remove `prompts/_legacy/` fallback source path from `scripts/migrate_prompts_layout.py`.
- [x] Update prompt-loader tests to enforce strict scenario prompt resolution.

## Batch 6.0: Scenario IO Extraction (Completed)

- [x] Extract all `build_*_prompt` and `collect_*_score` helpers from `run_race.py` into `race/scenario_io.py`.
- [x] Switch `run_race.py` call sites to `race_scenario_io.*` helpers (no behavior changes).
- [x] Add dedicated tests for extracted scenario helpers in `tests/test_race_scenario_io.py`.
- [x] Include scenario helper tests in CI contract coverage.

## Batch 6.1: Local-Mode Runner Consolidation (Completed)

- [x] Replace per-simulation no-server branches in `run_race.py` with one shared local-mode dispatch.
- [x] Add shared runner module `race/local_mode.py` for parallel launch, scoring, leaderboard, and persistence flow.
- [x] Resolve prompt/score helpers dynamically from scenario registry metadata (`prompt_code`, `cli_code`, `duration_arg`).
- [x] Add focused tests for local-mode runner behavior in `tests/test_race_local_mode.py`.

## Batch 6.2: Server-Mode Runner Consolidation (Completed)

- [x] Extract vending-machine server orchestration into `race/server_mode.py`.
- [x] Replace inline server mode branch in `run_race.py` with a shared runner call.
- [x] Add focused tests for server mode startup/teardown and happy path in `tests/test_race_server_mode.py`.
- [x] Include server mode runner tests in CI contract coverage.
