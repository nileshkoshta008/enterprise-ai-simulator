import datetime
from pydantic import BaseModel
from typing import Optional, Literal

class Email(BaseModel):
    id: str
    subject: str
    body: str
    sender_tier: Literal["bronze", "silver", "gold"]
    sla_hours: int  # e.g., Gold requires 2 hours, Bronze 48 hours
    time_elapsed_hours: float
    true_priority: Literal["low", "medium", "high", "critical"]
    true_category: Literal["billing", "technical", "spam", "general"]
    true_action: Literal["reply", "ignore", "escalate"]

class EnvState(BaseModel):
    task_tier: str = "easy"
    current_email_index: int = 0
    total_reward: float = 0.0

class Observation(BaseModel):
    email_subject: str
    email_body: str
    customer_tier: Literal["bronze", "silver", "gold"]
    sla_hours: int
    time_elapsed_hours: float
    state: Optional[EnvState] = None

class Action(BaseModel):
    priority: Literal["low", "medium", "high", "critical"]
    category: Literal["billing", "technical", "spam", "general"]
    decision: Literal["reply", "ignore", "escalate"]
    reasoning: Optional[str] = None

class Reward(BaseModel):
    score: float
    details: dict[str, float]
    penalty: float
