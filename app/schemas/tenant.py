import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    plan_tier: str | None = None
    status: str
    onboarding_state: str
    created_at: datetime

class TenantDetailResponse(TenantResponse):
    created_by: str | None = None
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    subscription_status: str | None = None
    updated_at: datetime

class TenantStatusUpdateRequest(BaseModel):
    status: Literal["active", "suspended"]

class OnboardingStateUpdateRequest(BaseModel):
    onboarding_state: Literal["created", "payment_pending", "configuring", "ready_for_testing", "pending_approval", "active", "past_due", "paused", "suspended", "closed"]
