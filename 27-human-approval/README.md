# Track 27: human-in-the-loop approval

`execute_stepwise()` pauses before every `read_only=False` primitive and yields
a checkpoint with status `AWAITING_APPROVAL`. The caller reads the pending call,
asks the user, then either resumes or abandons. The primitive only executes if
the user approves.

## Install

```bash
uv add opensymbolicai-core
```

## Running it

```bash
uv run main.py
```

```
============================================================
Task: Compose and send a project status update to alice@example.com.

  Pending: confirmation = send_email(email)
  To:      alice@example.com
  Subject: Project Status Update
  Body:    Please find the latest status update attached.

  Approve? [y/n]: y
Result: Sent to alice@example.com: 'Project Status Update'

Task: Compose and send a meeting cancellation to team@example.com.

  Pending: confirmation = send_email(email)
  To:      team@example.com
  Subject: Meeting Cancellation
  Body:    Unfortunately, we have had to cancel our meeting.

  Approve? [y/n]: n
Rejected — email not sent.
```

## What is happening

`require_mutation_approval=True` tells the framework to pause before any
`read_only=False` primitive. The call to `compose_email` runs uninterrupted
because it is `read_only=True`. The call to `send_email` triggers the pause.

```python
config = PlanExecuteConfig(require_mutation_approval=True)
agent = EmailAgent(llm=llm, config=config)

for cp in agent.execute_stepwise(task, serializer=_serializer):
    if cp.status == CheckpointStatus.AWAITING_APPROVAL:
        # inspect cp.pending_mutation, ask the user
        if approved:
            for cp2 in agent.resume_from_checkpoint(cp, approve_mutation=True, serializer=_serializer):
                ...
        else:
            # don't call resume_from_checkpoint — execution is abandoned
```

The checkpoint's `namespace_snapshot` holds all variables computed so far
(here, the composed `Email`). Passing a `SerializerRegistry` with `Email`
registered lets the framework deserialize those variables when resuming, so
the plan picks up exactly where it left off.

`result_value.data` on the completed checkpoint is the raw serialized result —
for a string return type, that is the string itself.
