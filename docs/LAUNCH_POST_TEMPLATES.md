# Launch Post Templates

Use these as copy-ready starting points. Replace bracketed placeholders.

## Shared Facts to Include

- Open-source repo: `https://github.com/humancto/simulation-crucible`
- Scope: behavioral experiment platform, not an ultimate benchmark
- Current coverage snapshot: `[X]/50 simulations with published artifacts`
- Repro command: `python3 scripts/doctor.py --skip-agents`

## LinkedIn Template

```text
Open-sourcing: The Simulation Crucible

We built an AI behavioral experiment platform to test how models handle tradeoffs, hidden metrics, and ethical pressure across synthetic scenarios.

What it is:
- 50 scenario framework with shared scoring + constraint variants
- reproducible race runner + artifact manifests
- fairness disparity metrics in selected scenarios

What it is not:
- not an ultimate benchmark
- not deployment safety certification

Why this matters:
- teams can run due diligence with transparent artifacts
- contributors can add simulations and evaluation logic in a consistent way

Repo: https://github.com/humancto/simulation-crucible
Quick check: python3 scripts/doctor.py --skip-agents
Protocol: docs/EVALUATION_PROTOCOL.md

If you work on model evals, red-team workflows, or safety tooling, would value your feedback and PRs.
```

## Product Hunt Template

```text
The Simulation Crucible is an open-source behavioral stress-test framework for AI agents.

It lets you run models through synthetic scenarios with hidden metrics and constraint variants, then compare behavior with reproducible artifacts.

Built for:
- comparative model evals
- regression tracking
- fairness/harm signal analysis

Not positioned as a universal benchmark or certification suite.

GitHub: https://github.com/humancto/simulation-crucible
Clone-and-run check: python3 scripts/doctor.py --skip-agents
Contributing path: docs/CONTRIBUTOR_TASK_BOARD.md
```

## Reddit Template

```text
I open-sourced a project called Simulation Crucible:
https://github.com/humancto/simulation-crucible

It is a behavioral eval framework for AI agents (synthetic scenarios + hidden metrics + constraint variants).

Trying to keep claims realistic:
- useful for relative comparisons and failure analysis
- not a universal benchmark or deployment cert

If you want to poke holes in it, please do.
I added protocol + release checklist docs to make methodology explicit:
- docs/EVALUATION_PROTOCOL.md
- docs/RELEASE_CHECKLIST.md

Would appreciate critique on scenario quality, fairness metrics, and what baseline policies should be mandatory.
```

## Release Note Snippet

```text
Release highlights:
- Added evaluation protocol and release checklist docs
- Added contributor task board for workstream-based PRs
- Added results coverage script + tests for artifact transparency
- Updated docs and site links to reflect scope and reproducibility standards

Known limitations:
- artifact coverage is currently partial across the full scenario bank
- results should be treated as comparative signals, not absolute truth
```
