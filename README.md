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
