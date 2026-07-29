from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import Principal, require_organization_admin
from app.db.database import get_db
from app.schemas.tenant import OnboardingStateUpdateRequest, TenantDetailResponse
from app.services.onboarding_service import OnboardingService

onboarding_router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

@onboarding_router.get("/status", response_model=TenantDetailResponse)
def get_onboarding_status(
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)],
) -> TenantDetailResponse:
    service = OnboardingService(database)
    tenant = service.get_status(principal)
    
    return TenantDetailResponse(
        id=tenant.id,
        name=tenant.name,
        plan_tier=tenant.plan_tier,
        status=tenant.status,
        onboarding_state=tenant.onboarding_state,
        created_at=tenant.created_at,
        created_by=tenant.created_by,
        stripe_customer_id=tenant.stripe_customer_id,
        stripe_subscription_id=tenant.stripe_subscription_id,
        subscription_status=tenant.subscription_status,
        updated_at=tenant.updated_at,
    )

@onboarding_router.patch("/status", response_model=TenantDetailResponse)
def update_onboarding_status(
    payload: OnboardingStateUpdateRequest,
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)],
) -> TenantDetailResponse:
    service = OnboardingService(database)
    tenant = service.update_status(payload, principal)
        
    return TenantDetailResponse(
        id=tenant.id,
        name=tenant.name,
        plan_tier=tenant.plan_tier,
        status=tenant.status,
        onboarding_state=tenant.onboarding_state,
        created_at=tenant.created_at,
        created_by=tenant.created_by,
        stripe_customer_id=tenant.stripe_customer_id,
        stripe_subscription_id=tenant.stripe_subscription_id,
        subscription_status=tenant.subscription_status,
        updated_at=tenant.updated_at,
    )
