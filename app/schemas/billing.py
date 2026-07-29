from pydantic import BaseModel

class CheckoutSessionRequest(BaseModel):
    plan_tier: str
    success_url: str
    cancel_url: str

class SubscriptionStatusResponse(BaseModel):
    plan_tier: str | None
    status: str | None
    current_period_end: int | None
    cancel_at_period_end: bool | None

class PortalSessionRequest(BaseModel):
    return_url: str

class PortalSessionResponse(BaseModel):
    url: str

class UpgradePlanRequest(BaseModel):
    plan_tier: str

class InvoiceItem(BaseModel):
    id: str
    amount_due: int
    amount_paid: int
    status: str | None
    invoice_pdf: str | None
    created: int

class InvoiceListResponse(BaseModel):
    invoices: list[InvoiceItem]
