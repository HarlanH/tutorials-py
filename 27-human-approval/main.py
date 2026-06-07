"""Human-in-the-loop mutation approval.

execute_stepwise() pauses at every read_only=False primitive and yields a
checkpoint with status AWAITING_APPROVAL. The caller inspects the pending
call, asks the user y/n, then either resumes or abandons.

Usage:
    uv run main.py
"""

from __future__ import annotations

from emailer import Email, EmailAgent
from ollama import check_ollama

from opensymbolicai.checkpoint import CheckpointStatus, ExecutionCheckpoint, SerializerRegistry
from opensymbolicai.llm import LLMConfig
from opensymbolicai.models import PlanExecuteConfig

# Register Email so the namespace can be restored when resuming from a checkpoint.
_serializer = SerializerRegistry()
_serializer.register(
    Email,
    serializer=lambda e: e.model_dump(),
    deserializer=lambda d: Email(**d),
)

TASKS = [
    "Compose and send a project status update to alice@example.com.",
    "Compose and send a meeting cancellation to team@example.com.",
]


def _email_from_checkpoint(cp: ExecutionCheckpoint) -> dict | None:
    """Pull the Email data out of the namespace snapshot."""
    var_name = cp.pending_mutation.args.get("email", cp.pending_mutation.args.get("arg0"))
    candidates = (
        [cp.namespace_snapshot[var_name]]
        if var_name and var_name in cp.namespace_snapshot
        else list(cp.namespace_snapshot.values())
    )
    for sv in candidates:
        if not isinstance(sv.data, dict):
            continue
        # Custom serializer: flat dict {"to": ..., "subject": ..., "body": ...}
        if "to" in sv.data and "subject" in sv.data:
            return sv.data
        # Default pydantic format: {"__pydantic__": True, "data": {...}}
        inner = sv.data.get("data")
        if isinstance(inner, dict) and "to" in inner and "subject" in inner:
            return inner
    return None


def run(llm: LLMConfig, task: str) -> None:
    config = PlanExecuteConfig(require_mutation_approval=True)
    agent = EmailAgent(llm=llm, config=config)

    print(f"Task: {task}")

    for cp in agent.execute_stepwise(task, serializer=_serializer):
        if cp.status != CheckpointStatus.AWAITING_APPROVAL:
            continue

        m = cp.pending_mutation
        email = _email_from_checkpoint(cp)

        print(f"\n  Pending: {m.statement}")
        if email:
            print(f"  To:      {email['to']}")
            print(f"  Subject: {email['subject']}")
            print(f"  Body:    {email['body']}")

        answer = input("\n  Approve? [y/n]: ").strip().lower()

        if answer == "y":
            for cp2 in agent.resume_from_checkpoint(cp, approve_mutation=True, serializer=_serializer):
                if cp2.status == CheckpointStatus.COMPLETED and cp2.result_value:
                    print(f"\nResult: {cp2.result_value.data}")
        else:
            print("\nRejected — email not sent.")

        break

    print()


def main() -> None:
    model = "qwen2.5-coder:7b"
    if not check_ollama(model):
        return

    llm = LLMConfig(provider="ollama", model=model)

    print("=" * 60)
    for task in TASKS:
        run(llm, task)


if __name__ == "__main__":
    main()
