import stripe

# Set your secret key: remember to switch to your live secret key in production!
stripe.api_key = "sk_test_51PmKaBP94pbCvQFRSPQIAcWeSTBCbjr5RB2M5FrzvzfOdkUPOHpc9u2fYD2mp6fNHsyy7kzgyw3obSh4RIw00GJQ00KE7tQv6l"

def process_payment(order, payment_data):
    """
    Processes the payment using Stripe.

    Args:
        order: The order instance that needs to be paid for.
        payment_data: A dictionary containing the payment details (e.g., stripe_token).

    Returns:
        A dictionary with 'status' and optionally 'charge_id' or 'message'.
    """
    try:
        # Create a charge: this will charge the user's card
        charge = stripe.Charge.create(
            amount=int(order.TotalAmount * 100),  # Amount in cents
            currency="usd",
            source=payment_data['stripe_token'],  # Obtained with Stripe.js
            description=f"Payment for order {order.id}"
        )
        return {'status': 'success', 'charge_id': charge.id}
    except stripe.error.CardError as e:
        # The card has been declined
        return {'status': 'error', 'message': str(e)}
    except stripe.error.StripeError as e:
        # Handle other types of Stripe errors
        return {'status': 'error', 'message': "Something went wrong with your payment. Please try again later."}
    except Exception as e:
        # Handle other unexpected errors
        return {'status': 'error', 'message': str(e)}
