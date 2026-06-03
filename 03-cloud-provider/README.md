# Track 3: Swap to a cloud provider

The same agent runs on a hosted provider. Provider, model, and API key all live
in `.env`, so moving between providers is a config change, not a code change.

## Configure

Copy the template and fill in the key for your provider:

```bash
cp .env.example .env
```

`.env` sets which provider and model to use, plus the matching API key:

```bash
LLM_PROVIDER=fireworks
LLM_MODEL=accounts/fireworks/models/gpt-oss-120b
FIREWORKS_API_KEY=fw_...
```

[`main.py`](main.py) reads all three from the environment. The
[`calculator.py`](calculator.py) agent, its primitives, and the task are
unchanged from Track 1.

## Run it

```bash
uv run main.py
```

Output:

```
53
```

## Switch providers

Edit `.env`. To use OpenAI instead of Fireworks, change two lines and set the
matching key:

```diff
- LLM_PROVIDER=fireworks
- LLM_MODEL=accounts/fireworks/models/gpt-oss-120b
+ LLM_PROVIDER=openai
+ LLM_MODEL=gpt-4.1-nano
```

| Provider  | `LLM_PROVIDER` | Example `LLM_MODEL`       | Key env var         |
|-----------|----------------|---------------------------|---------------------|
| OpenAI    | `openai`       | `gpt-4.1-nano`            | `OPENAI_API_KEY`    |
| Anthropic | `anthropic`    | `claude-haiku-4-5`        | `ANTHROPIC_API_KEY` |
| Groq      | `groq`         | `llama-3.3-70b-versatile` | `GROQ_API_KEY`      |
| Fireworks | `fireworks`    | `accounts/fireworks/models/gpt-oss-120b` | `FIREWORKS_API_KEY` |

Model names change over time, so check the provider's own list for current
options.

## Takeaway

The agent is decoupled from the provider. Local or cloud, Fireworks or OpenAI,
the choice is configuration. Your primitives, plan logic, and task stay put.
