import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import Principal, get_current_principal, require_organization_admin
from app.db.database import get_db
from app.schemas.invitation import InvitationAccept, InvitationCreate, InvitationResponse
from app.services.identity_service import IdentityService
from app.schemas.domain import RegistrationResponse
from app.routers.auth import db_user_to_authenticated

invitations_router = APIRouter(prefix="/api/invitations", tags=["invitations"])

def get_identity_service(session: Annotated[Session, Depends(get_db)]) -> IdentityService:
    return IdentityService(session)

@invitations_router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(
    payload: InvitationCreate,
    principal: Annotated[Principal, Depends(require_organization_admin)],
    identity_service: Annotated[IdentityService, Depends(get_identity_service)],
) -> InvitationResponse:
    if not principal.tenant_id:
        raise ApiError(403, "FORBIDDEN", "You must belong to an organization to invite users.")

    tenant_id = uuid.UUID(principal.tenant_id)
    invitation = identity_service.invite_user(
        tenant_id=tenant_id,
        email=payload.email
    )
    return invitation

@invitations_router.post("/accept", response_model=RegistrationResponse, status_code=status.HTTP_200_OK)
def accept_invitation(
    payload: InvitationAccept,
    identity_service: Annotated[IdentityService, Depends(get_identity_service)],
) -> RegistrationResponse:
    user = identity_service.accept_invitation(
        token=payload.token,
        password=payload.password,
        full_name=payload.full_name
    )
    return RegistrationResponse(user=db_user_to_authenticated(user))
