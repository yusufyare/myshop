import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

@csrf_exempt
def stripe_webhook(request):
    print("HELLO! STRIPE IS TALKING TO ME!")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                # Ensure client_reference_id was passed when creating the session
                order = Order.objects.get(id=session.client_reference_id)
                order.paid = True
                order.stripe_id = session.payment_intent
                
                order.save() # Fixed the typo here
            except Order.DoesNotExist:
                return HttpResponse(status=404)

    return HttpResponse(status=200)