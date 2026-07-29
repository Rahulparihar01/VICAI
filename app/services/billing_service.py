import uuid

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.stripe_client import get_stripe_client
from app.models.tenant import Tenant

settings = get_settings()

PRICE_MAP = {
    "starter": "price_starter_placeholder",
    "growth": "price_growth_placeholder",
    "pro": "price_pro_placeholder",
}

def create_checkout_session(
    db: Session,
    tenant_id: uuid.UUID,
    plan_tier: str,
    success_url: str,
    cancel_url: str
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")
        
    if plan_tier == "enterprise":
        raise ValueError("Enterprise plan requires a custom quote, please contact sales.")
        
    if plan_tier not in PRICE_MAP:
        raise ValueError(f"Invalid plan tier: {plan_tier}")

    price_id = PRICE_MAP[plan_tier]
    stripe_client = get_stripe_client()
    
    customer_id = tenant.stripe_customer_id
    if not customer_id:
        customer = stripe_client.Customer.create(
            name=tenant.name,
            metadata={"tenant_id": str(tenant.id)}
        )
        customer_id = customer.id
        tenant.stripe_customer_id = customer_id
        db.commit()

    session = stripe_client.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(tenant.id)
    )
    
    tenant.plan_tier = plan_tier
    db.commit()
    
    return session.url

def process_webhook_event(db: Session, payload: bytes, sig_header: str):
    stripe_client = get_stripe_client()
    try:
        secret_str = settings.stripe_webhook_secret
        secret = secret_str.get_secret_value() if secret_str else ""
        event = stripe_client.Webhook.construct_event(payload, sig_header, secret)
    except stripe_client.error.SignatureVerificationError as e:
        raise ValueError(f"Invalid webhook signature") from e
    except Exception as e:
        raise ValueError(f"Webhook error: {str(e)}") from e

    if event.type == 'checkout.session.completed':
        session = event.data.object
        try:
            tenant_id_str = getattr(session, 'client_reference_id', None)
            
            # Development fallback: If testing with `stripe trigger`, client_reference_id is usually null.
            if not tenant_id_str and settings.vicai_env == "development":
                first_tenant = db.query(Tenant).first()
                if first_tenant:
                    tenant_id_str = str(first_tenant.id)
                    print(f"DEV MODE: Using fallback tenant {tenant_id_str} for testing webhook.")

            if tenant_id_str:
                tenant = db.query(Tenant).filter(Tenant.id == uuid.UUID(tenant_id_str)).first()
                if tenant:
                    tenant.stripe_subscription_id = getattr(session, 'subscription', None)
                    tenant.subscription_status = 'active'
                    if tenant.onboarding_state in ('created', 'payment_pending'):
                        tenant.onboarding_state = 'configuring'
                    db.commit()
                    
                    from app.repositories.audit_log_repo import AuditLogRepository
                    audit_repo = AuditLogRepository(db)
                    # We don't have a specific actor_id since this is a webhook, 
                    # we can use a zero UUID or the tenant's creator. Let's use a zero UUID for system actions.
                    system_uuid = uuid.UUID(int=0)
                    audit_repo.create(
                        actor_id=system_uuid,
                        action="subscription_activated",
                        resource_type="tenant",
                        resource_id=str(tenant.id),
                        tenant_id=tenant.id,
                        details={"subscription_id": tenant.stripe_subscription_id}
                    )
                    db.commit()
                    
                    print(f"SUCCESS: Tenant {tenant.name} subscription activated via webhook!")
        except Exception as e:
            err_msg = f"Error processing checkout session: {type(e).__name__} - {str(e)}"
            raise ValueError(err_msg) from e

    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        customer_id = getattr(subscription, 'customer', None)
        if customer_id:
            tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == customer_id).first()
            if tenant:
                tenant.subscription_status = getattr(subscription, 'status', None)
                if tenant.subscription_status in ('past_due', 'unpaid'):
                    tenant.onboarding_state = 'past_due'
                elif tenant.subscription_status == 'active' and tenant.onboarding_state == 'past_due':
                    tenant.onboarding_state = 'active' # Revert back to active
                db.commit()

    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        customer_id = getattr(subscription, 'customer', None)
        if customer_id:
            tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == customer_id).first()
            if tenant:
                tenant.subscription_status = 'canceled'
                tenant.onboarding_state = 'suspended'
                db.commit()

    return True

def get_subscription_status(db: Session, tenant_id: uuid.UUID):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")
        
    status = {
        "plan_tier": tenant.plan_tier,
        "status": tenant.subscription_status,
        "current_period_end": None,
        "cancel_at_period_end": None,
    }
    
    if tenant.stripe_subscription_id:
        stripe_client = get_stripe_client()
        try:
            sub = stripe_client.Subscription.retrieve(tenant.stripe_subscription_id)
            status["status"] = sub.status
            status["current_period_end"] = sub.current_period_end
            status["cancel_at_period_end"] = sub.cancel_at_period_end
            
            # Sync to DB if changed
            if tenant.subscription_status != sub.status:
                tenant.subscription_status = sub.status
                db.commit()
        except Exception as e:
            print(f"Error fetching subscription from Stripe: {e}")
            
    return status

def create_customer_portal_session(db: Session, tenant_id: uuid.UUID, return_url: str):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")
        
    if not tenant.stripe_customer_id:
        raise ValueError("Tenant does not have a Stripe customer ID")
        
    stripe_client = get_stripe_client()
    try:
        session = stripe_client.billing_portal.Session.create(
            customer=tenant.stripe_customer_id,
            return_url=return_url
        )
        return session.url
    except Exception as e:
        raise ValueError(f"Error creating portal session: {str(e)}") from e

def update_subscription_plan(db: Session, tenant_id: uuid.UUID, new_plan_tier: str):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")
        
    if not tenant.stripe_subscription_id:
        raise ValueError("Tenant does not have an active subscription")
        
    if new_plan_tier == "enterprise":
        raise ValueError("Enterprise plan requires a custom quote, please contact sales.")
        
    if new_plan_tier not in PRICE_MAP:
        raise ValueError(f"Invalid plan tier: {new_plan_tier}")

    price_id = PRICE_MAP[new_plan_tier]
    stripe_client = get_stripe_client()
    
    try:
        sub = stripe_client.Subscription.retrieve(tenant.stripe_subscription_id)
        # Assuming the subscription has only one item for the base plan
        item_id = sub.items.data[0].id
        
        stripe_client.Subscription.modify(
            tenant.stripe_subscription_id,
            items=[{
                "id": item_id,
                "price": price_id,
            }],
            proration_behavior="create_prorations"
        )
        
        tenant.plan_tier = new_plan_tier
        db.commit()
        return True
    except Exception as e:
        raise ValueError(f"Error updating subscription: {str(e)}") from e

def get_invoices(db: Session, tenant_id: uuid.UUID, limit: int = 10):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")
        
    if not tenant.stripe_customer_id:
        return []
        
    stripe_client = get_stripe_client()
    try:
        invoices = stripe_client.Invoice.list(
            customer=tenant.stripe_customer_id,
            limit=limit
        )
        
        result = []
        for inv in invoices.data:
            result.append({
                "id": inv.id,
                "amount_due": inv.amount_due,
                "amount_paid": inv.amount_paid,
                "status": inv.status,
                "invoice_pdf": inv.invoice_pdf,
                "created": inv.created,
            })
        return result
    except Exception as e:
        raise ValueError(f"Error fetching invoices: {str(e)}") from e
