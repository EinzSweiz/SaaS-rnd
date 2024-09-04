# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from decouple import config


DJANGO_DEBUG = config('DJANGO_DEBUG', cast=bool, default=False)
STRIPE_API_KEY = config('STRIPE_SECRET_KEY', cast=str, default=None)

if 'sk_test' in STRIPE_API_KEY and not DJANGO_DEBUG:
  raise ValueError('Invalid key for production mode')

stripe.api_key = STRIPE_API_KEY

def create_customer(
    name='',
    email='',
    metadata={},
    raw=False):
  response = stripe.Customer.create(
    name=name,
    email=email,
    metadata=metadata
  )
  if raw:
    return response
  strip_id = response.id
  return strip_id

def create_product(
    name='',
    metadata={},
    raw=False):
  response = stripe.Product.create(
    name=name,
    metadata=metadata
  )
  if raw:
    return response
  strip_id = response.id
  return strip_id


def create_price(
    currency='usd',
    unit_amount='9999',
    interval= 'month',
    product=None,
    metadata={},
    raw=False
):
  if product is None:
    return None
  response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        recurring={'interval': interval},
        product=product,
        metadata=metadata
        )
  if raw:
    return response
  strip_id = response.id
  return response.id