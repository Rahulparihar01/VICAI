import uuid
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import Principal
from app.models.tenant import Tenant
from app.schemas.tenant import OnboardingStateUpdateRequest
from app.repositories.audit_log_repo import AuditLogRepository

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db

    def get_status(self, principal: Principal) -> Tenant:
        if not principal.tenant_id:
            raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
            
        try:
            t_uuid = uuid.UUID(principal.tenant_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid tenant ID.")
            
        tenant = self.db.get(Tenant, t_uuid)
        if not tenant:
            raise ApiError(404, "NOT_FOUND", "Tenant not found.")
            
        return tenant

    def update_status(self, payload: OnboardingStateUpdateRequest, principal: Principal) -> Tenant:
        if not principal.tenant_id:
            raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
            
        try:
            t_uuid = uuid.UUID(principal.tenant_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid tenant ID.")
            
        tenant = self.db.get(Tenant, t_uuid)
        if not tenant:
            raise ApiError(404, "NOT_FOUND", "Tenant not found.")
            
        allowed_transitions = [
            ("configuring", "ready_for_testing"),
            ("ready_for_testing", "pending_approval"),
            ("configuring", "pending_approval")
        ]
        
        if payload.onboarding_state != tenant.onboarding_state:
            transition = (tenant.onboarding_state, payload.onboarding_state)
            
            reverse_transitions = [
                ("ready_for_testing", "configuring"),
                ("pending_approval", "configuring")
            ]
            
            if transition not in allowed_transitions and transition not in reverse_transitions:
                raise ApiError(400, "BAD_REQUEST", f"Cannot transition onboarding state from {tenant.onboarding_state} to {payload.onboarding_state}")
                
            tenant.onboarding_state = payload.onboarding_state
            self.db.commit()
            self.db.refresh(tenant)
            
            audit_repo = AuditLogRepository(self.db)
            audit_repo.create(
                actor_id=uuid.UUID(principal.subject),
                action="onboarding_state_changed",
                resource_type="tenant",
                resource_id=str(tenant.id),
                tenant_id=tenant.id,
                details={"new_state": payload.onboarding_state},
            )
            self.db.commit()
            
        return tenant
