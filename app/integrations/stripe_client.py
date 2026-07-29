import stripe

from app.core.config import get_settings

settings = get_settings()

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key.get_secret_value()

def get_stripe_client():
    return stripe
