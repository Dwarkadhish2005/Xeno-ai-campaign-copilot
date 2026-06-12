from pydantic import BaseModel, Field
from typing import Any, Literal, Union, Optional
from datetime import datetime


# ─── Generic Envelope ─────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    success: bool
    data: dict[str, Any]
    message: str


class EmptyResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = ""


# ─── AI / Campaign Planning ────────────────────────────────────────────────────

class Filter(BaseModel):
    field: str = Field(..., description="Customer profile or customer field name")
    operator: Literal[">", "<", ">=", "<=", "=", "!="]
    value: Union[int, float, str] = Field(..., description="Filter value")


class CampaignPlan(BaseModel):
    audience_name: str
    filters: list[Filter]
    channel: Literal["whatsapp", "sms", "email", "rcs"]
    strategy: str
    reasoning: str


# ─── Campaign CRUD ─────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    business_goal: Optional[str] = None
    audience_name: Optional[str] = None
    filters: Optional[list[Filter]] = None
    channel: Literal["whatsapp", "sms", "email", "rcs"]
    strategy: Optional[str] = None
    ai_reasoning: Optional[str] = None
    message_template: Optional[str] = None
    subject_line: Optional[str] = None


class CampaignOut(BaseModel):
    id: int
    name: str
    audience_name: Optional[str] = None
    filters: Optional[Any] = None
    channel: str
    strategy: Optional[str] = None
    message_template: Optional[str] = None
    subject_line: Optional[str] = None
    status: str
    audience_size: int
    business_goal: Optional[str] = None
    ai_reasoning: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Audience ─────────────────────────────────────────────────────────────────

class AudiencePreviewRequest(BaseModel):
    filters: list[Filter]


class AudienceBuildRequest(BaseModel):
    campaign_id: int
    filters: list[Filter]


# ─── Analytics ────────────────────────────────────────────────────────────────

class WebhookCallback(BaseModel):
    campaign_id: int
    customer_id: int
    communication_log_id: int
    event: Literal["sent", "delivered", "opened", "clicked", "failed"]
    timestamp: datetime
