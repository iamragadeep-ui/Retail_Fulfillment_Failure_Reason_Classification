from dataclasses import asdict, dataclass
from typing import Optional
from uuid import uuid4


def generate_id(prefix: str) -> str:
    """
    Generate a readable unique identifier.
    """

    return f"{prefix}_{uuid4()}"


@dataclass
class TraceContext:
    """
    Correlation identifiers shared across one complete request.
    """

    request_id: str
    trace_id: str
    session_id: str
    user_id: str
    conversation_id: str
    agent_run_id: str
    current_span_id: Optional[str] = None

    @classmethod
    def create(
        cls,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> "TraceContext":
        """
        Create a new trace context for an incoming request.

        Existing session/user/conversation identifiers can be preserved
        when supplied by the application.
        """

        return cls(
            request_id=generate_id("req"),
            trace_id=generate_id("trace"),
            session_id=session_id or generate_id("session"),
            user_id=user_id or generate_id("user"),
            conversation_id=conversation_id or generate_id("conversation"),
            agent_run_id=generate_id("agent"),
        )

    def create_span_id(self) -> str:
        """
        Generate a unique span identifier.
        """

        return generate_id("span")

    def to_dict(self) -> dict:
        """
        Convert the trace context into a dictionary.
        """

        return asdict(self)