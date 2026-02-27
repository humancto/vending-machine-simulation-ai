# Release Ready Now

This is the shortest path to publishing this project responsibly.

## 1. What You Can Claim Today

- The framework is open-source and productionized for reproducible behavioral experiments.
- A complete codex `soft_guidelines` run exists across all 50 simulations.
- Results are published as artifacts with reproducibility metadata and summary tooling.

## 2. What You Must Not Claim Today

- Do not call this a universal benchmark.
- Do not claim deployment safety certification.
- Do not claim cross-variant conclusions until full `hard_rules` batch completes.

## 3. Current Status Snapshot (Feb 27, 2026)

- `soft_guidelines` codex campaign: `50/50` complete, `0` failures.
  - `results/campaigns/all_sims_soft_codex_20260224-180134/`
- `hard_rules` codex campaign: in progress (TODO track for this release).
  - `results/campaigns/all_sims_hard_codex_20260227-163429/`

## 4. 5-Minute Pre-Publish Check

```bash
python3 scripts/doctor.py --skip-agents
python3 scripts/results_coverage.py --results-glob "results/campaigns/all_sims_soft_codex_20260224-180134/*.json" --output /tmp/release_soft_coverage.json --quiet
python3 scripts/full_campaign.py --agents codex --variant soft_guidelines --limit 2 --dry-run --results-dir /tmp/release_campaign_dryrun
```

If all three commands pass, you are ready to publish the current release position.

## 5. Copy-Ready Short Post

```text
Open-sourcing: The Simulation Crucible

Simulation Crucible is an open behavioral experiment platform for AI agents.
It tests model behavior under synthetic scenarios with hidden metrics, ethical pressure, and constraint variants.

Current release snapshot:
- 50-scenario framework with reproducible runner flow
- complete codex soft_guidelines batch across all 50 scenarios (artifacts published)
- hard_rules full batch is in progress and explicitly tracked as TODO

Not an ultimate benchmark. Not deployment safety certification.

Repo: https://github.com/humancto/simulation-crucible
Protocol: docs/EVALUATION_PROTOCOL.md
Release packet: docs/RELEASE_PACKET.md
Contribute: docs/CONTRIBUTOR_TASK_BOARD.md
```

## 6. Post-Release TODO

- Finish `hard_rules` full campaign and publish matching coverage/summaries.
- Add one additional agent full campaign for cross-agent comparative credibility.
- Publish a variant comparison brief after both variant batches are complete.

## 7. Why Someone Should Run This

- To compare behavioral tradeoffs under identical conditions, not just raw task completion.
- To detect regressions and policy sensitivity with reproducible artifacts.
- To inspect hidden-metric failures that typical benchmark scores miss.
- To support due diligence with transparent methodology instead of black-box claims.

## 8. Research and Community Value

- Creates an open scenario bank for behavioral-eval experimentation.
- Makes it easy to contribute new simulations with shared runner contracts.
- Enables publishable analysis workflows (seed sweeps, summaries, regression gates).
- Keeps the project fun and exploratory while preserving clear claim boundaries.
