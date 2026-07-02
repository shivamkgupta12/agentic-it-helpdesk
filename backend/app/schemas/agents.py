from typing import Literal

from pydantic import BaseModel, Field


ITCategory = Literal[
    "Network / VPN",
    "Password / Account",
    "Software Request",
    "Hardware Issue",
    "Email / Outlook",
    "Access Request",
    "Security Incident",
    "Cloud / Account Access",
    "General IT Query",
]

PriorityLevel = Literal["Low", "Medium", "High", "Critical"]


class TriageResult(BaseModel):
    category: ITCategory = "General IT Query"
    priority: PriorityLevel = "Medium"
    urgency: PriorityLevel = "Medium"
    needs_clarification: bool = False
    clarifying_question: str | None = None
    ticket_required: bool = False
    sensitive_action: bool = False


class AgentTraceStep(BaseModel):
    agent_name: str
    input_summary: str | None = None
    output_summary: str | None = None
    metadata: dict = Field(default_factory=dict)