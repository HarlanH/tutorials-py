"""Email agent with a read-only compose step and a mutating send step.

compose_email is read_only=True — it never triggers approval.
send_email is read_only=False — execution pauses here for human review.
"""

from __future__ import annotations

from pydantic import BaseModel

from opensymbolicai.blueprints import PlanExecute
from opensymbolicai.core import primitive


class Email(BaseModel):
    to: str
    subject: str
    body: str


_OUTBOX: list[Email] = []


class EmailAgent(PlanExecute):
    """Composes and sends emails — with human approval before each send."""

    @primitive(read_only=True)
    def compose_email(self, to: str, subject: str, body: str) -> Email:
        """Compose a draft email. Does not send — returns an Email object."""
        return Email(to=to, subject=subject, body=body)

    @primitive(read_only=False)
    def send_email(self, email: Email) -> str:
        """Send the email and return a confirmation string."""
        _OUTBOX.append(email)
        return f"Sent to {email.to}: '{email.subject}'"
