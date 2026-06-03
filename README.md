# OpenSymbolicAI Tutorials (Python)

Hands-on tutorial tracks for [OpenSymbolicAI](https://pypi.org/project/opensymbolicai-core/),
taking you from "first five minutes" to "production-ready agent."

Each track is a **self-contained project**: its own folder, its own
`pyproject.toml`, its own runnable code. Pick a track, `cd` into it, and run it.

```bash
cd 01-hello
uv run main.py
```

## Tracks

| # | Track |
|---|-------|
| 01 | [Hello, OpenSymbolicAI](01-hello/): the five-minute first win |
| 02 | [Swap the local model](02-swap-model/): run Track 1's agent on a different model |
| 03 | [Swap to a cloud provider](03-cloud-provider/): run the same agent on a hosted provider |
| 04 | [What `@primitive` actually does](04-primitive-gate/): the gate that makes a method callable |
| 05 | [`read_only`](05-read-only/): the flag that signals whether a primitive modifies state |
| 06 | [`deterministic`](06-deterministic/): the flag that signals whether a primitive is pure |
| 07 | [Type annotations are the contract](07-type-contract/): how parameter and return types reach the LLM |
| 08 | [Read the generated plan](08-read-the-plan/): the Python the LLM wrote, in `result.plan` |
| 09 | [Read the execution trace](09-read-the-trace/): the plan after it ran, step by step, in `result.trace` |
| 10 | [Read the metrics](10-read-the-metrics/): what a run cost in time and tokens, in `result.metrics` |
| 11 | [Plan without executing](11-plan-without-executing/): generate a plan with `agent.plan`, review it, then run it |
| 12 | [Execute a plan you already have](12-execute-a-plan/): pass plan text to `agent.execute`, validation and all |
| 13 | [Analyze a plan's structure](13-analyze-a-plan/): read the primitive calls and `read_only` flags with `agent.analyze_plan` |
