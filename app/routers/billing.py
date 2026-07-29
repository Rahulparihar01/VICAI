import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import Principal, require_organization_admin
from app.db.database import get_db
from app.schemas.billing import (
    CheckoutSessionRequest,
    SubscriptionStatusResponse,
    PortalSessionRequest,
    PortalSessionResponse,
    UpgradePlanRequest,
    InvoiceListResponse,
)
from app.services.billing_service import (
    create_checkout_session,
    process_webhook_event,
    get_subscription_status,
    create_customer_portal_session,
    update_subscription_plan,
    get_invoices,
)

billing_router = APIRouter(prefix="/api/billing", tags=["billing"])

@billing_router.post("/create-checkout-session")
def api_create_checkout_session(
    payload: CheckoutSessionRequest,
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)]
):
    if not principal.tenant_id:
        raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
        
    try:
        url = create_checkout_session(
            db=database,
            tenant_id=uuid.UUID(principal.tenant_id),
            plan_tier=payload.plan_tier,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url
        )
        return {"url": url}
    except ValueError as e:
        raise ApiError(400, "BAD_REQUEST", str(e))

@billing_router.post("/webhook")
async def api_webhook(request: Request, database: Annotated[Session, Depends(get_db)]):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    print(f"WEBHOOK RECEIVED. Sig header: {sig_header}")
    print(f"Payload length: {len(payload)}")
    
    try:
        process_webhook_event(database, payload, sig_header)
        return {"status": "success"}
    except ValueError as e:
        print(f"WEBHOOK ERROR: {str(e)}")
        raise ApiError(400, "BAD_REQUEST", str(e))

@billing_router.get("/subscription", response_model=SubscriptionStatusResponse)
def api_get_subscription(
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)]
):
    if not principal.tenant_id:
        raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
        
    try:
        status = get_subscription_status(database, uuid.UUID(principal.tenant_id))
        return SubscriptionStatusResponse(**status)
    except ValueError as e:
        raise ApiError(400, "BAD_REQUEST", str(e))

@billing_router.post("/portal", response_model=PortalSessionResponse)
def api_create_portal_session(
    payload: PortalSessionRequest,
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)]
):
    if not principal.tenant_id:
        raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
        
    try:
        url = create_customer_portal_session(database, uuid.UUID(principal.tenant_id), payload.return_url)
        return PortalSessionResponse(url=url)
    except ValueError as e:
        raise ApiError(400, "BAD_REQUEST", str(e))

@billing_router.post("/upgrade")
def api_upgrade_plan(
    payload: UpgradePlanRequest,
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)]
):
    if not principal.tenant_id:
        raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
        
    try:
        update_subscription_plan(database, uuid.UUID(principal.tenant_id), payload.plan_tier)
        return {"status": "success"}
    except ValueError as e:
        raise ApiError(400, "BAD_REQUEST", str(e))

@billing_router.get("/invoices", response_model=InvoiceListResponse)
def api_get_invoices(
    principal: Annotated[Principal, Depends(require_organization_admin)],
    database: Annotated[Session, Depends(get_db)]
):
    if not principal.tenant_id:
        raise ApiError(403, "FORBIDDEN", "User does not belong to a tenant.")
        
    try:
        invoices = get_invoices(database, uuid.UUID(principal.tenant_id))
        return InvoiceListResponse(invoices=invoices)
    except ValueError as e:
        raise ApiError(400, "BAD_REQUEST", str(e))
