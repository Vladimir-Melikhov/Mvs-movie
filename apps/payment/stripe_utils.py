import stripe
from typing import Optional, Dict, Any
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import StripeCustomer

User = get_user_model()

                          
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_stripe_customer(user: User) -> str:
    try:
                                          
        stripe_customer = StripeCustomer.objects.get(user=user)
        return stripe_customer.stripe_customer_id
    except StripeCustomer.DoesNotExist:
                                    
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name() or user.username,
            metadata={
                'user_id': user.id,
                'username': user.username,
            }
        )

                          
        stripe_customer = StripeCustomer.objects.create(
            user=user,
            stripe_customer_id=customer.id
        )

        return customer.id


def create_checkout_session(
    user: User,
    success_url: str,
    cancel_url: str,
    subscription_months: int = 1
) -> Dict[str, Any]:
                                   
    customer_id = get_or_create_stripe_customer(user)

                                         
    amount = 1200 * subscription_months                   

    try:
                                 
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': amount,
                    'product_data': {
                        'name': f'VideoHub Premium Subscription ({subscription_months} month{"s" if subscription_months > 1 else ""})',
                        'description': f'Unlimited movie watching for {subscription_months} month{"s" if subscription_months > 1 else ""}',
                        'images': [settings.SITE_URL + '/static/images/logo.png'] if hasattr(settings, 'SITE_URL') else [],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user.id,
                'subscription_months': subscription_months,
            },
        )

        return {
            'session_id': session.id,
            'session_url': session.url,
            'customer_id': customer_id,
        }

    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create checkout session: {str(e)}")


def retrieve_checkout_session(session_id: str) -> Optional[stripe.checkout.Session]:
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError:
        return None


def retrieve_payment_intent(payment_intent_id: str) -> Optional[stripe.PaymentIntent]:
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except stripe.error.StripeError:
        return None


def construct_webhook_event(payload: bytes, sig_header: str) -> Optional[stripe.Event]:
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
                         
        return None
    except stripe.error.SignatureVerificationError:
                           
        return None


def refund_payment(payment_intent_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
    try:
        refund_params = {'payment_intent': payment_intent_id}
        if amount:
            refund_params['amount'] = amount

        refund = stripe.Refund.create(**refund_params)

        return {
            'success': True,
            'refund_id': refund.id,
            'status': refund.status,
            'amount': refund.amount,
        }

    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e),
        }