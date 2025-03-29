import stripe
from flask import Flask, render_template, request, jsonify, redirect
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Initialize Flask app
app = Flask(__name__,
            static_url_path='',
            static_folder='static')

# Stripe Configuration
stripe.api_key = os.getenv("STRIPE_API_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_PHONE = os.getenv("USER_PHONE")

# Your domain configuration
YOUR_DOMAIN = 'http://localhost:5000'

def send_sms(amount=50.00):
    """Function to send SMS using Twilio"""
    try:
        # Verify Twilio credentials and phone numbers
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, USER_PHONE]):
            missing_vars = []
            if not TWILIO_ACCOUNT_SID: missing_vars.append("TWILIO_ACCOUNT_SID")
            if not TWILIO_AUTH_TOKEN: missing_vars.append("TWILIO_AUTH_TOKEN")
            if not TWILIO_PHONE_NUMBER: missing_vars.append("TWILIO_PHONE_NUMBER")
            if not USER_PHONE: missing_vars.append("USER_PHONE")
            raise ValueError(f"Missing required Twilio configuration: {', '.join(missing_vars)}")
            
        print("\n=== Twilio Configuration ===")
        print(f"Account SID: {TWILIO_ACCOUNT_SID[:6]}...{TWILIO_ACCOUNT_SID[-4:]}")
        print(f"Auth Token: {TWILIO_AUTH_TOKEN[:6]}...{TWILIO_AUTH_TOKEN[-4:]}")
        print(f"From Number: {TWILIO_PHONE_NUMBER}")
        print(f"To Number: {USER_PHONE}")
        
        # Create Twilio client with the correct credentials
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
        print("\n=== Attempting to send SMS ===")
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=f"Payment of ${amount:.2f} Successful! Thank you for your purchase.",
            to=USER_PHONE
        )
        
        print(f"\n=== SMS Sent Successfully ===")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"Direction: {message.direction}")
        print(f"Date Created: {message.date_created}")
        
        # Check for any error codes
        if hasattr(message, 'error_code') and message.error_code:
            print(f"\nWarning: Message has error code: {message.error_code}")
            print(f"Error message: {message.error_message}")
            return False
            
        return True
        
    except Exception as e:
        print(f"\n=== Error Sending SMS ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        # Check for specific Twilio errors
        if hasattr(e, 'code'):
            print(f"Twilio Error Code: {e.code}")
        if hasattr(e, 'msg'):
            print(f"Twilio Error Message: {e.msg}")
            
        return False

@app.route("/")
def home():
    return render_template("index.html", key=STRIPE_PUBLIC_KEY)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Test Product"},
                    "unit_amount": 5000,  # $50.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=YOUR_DOMAIN + "/success?payment_status=completed&amount=50.00&transaction_id={CHECKOUT_SESSION_ID}",
            cancel_url=YOUR_DOMAIN + "/cancel",
            metadata={"phone": USER_PHONE}  # Store phone number in metadata
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return str(e), 400

@app.route("/pay", methods=["POST"])
def pay():
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Test Product"},
                    "unit_amount": 5000,  # $50.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=YOUR_DOMAIN + "/success?payment_status=completed&amount=50.00&transaction_id={CHECKOUT_SESSION_ID}",
            cancel_url=YOUR_DOMAIN + "/cancel",
            metadata={"phone": USER_PHONE}  # Store phone number in metadata
        )
        
        # Return the session ID to the frontend
        return jsonify({
            "id": session.id,
            "success_url": session.success_url
        })
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return str(e), 400

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    # Get the webhook payload and signature header
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    print("\n=== Webhook Request Received ===")
    print(f"Signature Header: {sig_header[:20]}...")
    print(f"Payload Length: {len(payload)} bytes")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
        print(f"\n=== Webhook Verified Successfully ===")
        print(f"Event Type: {event['type']}")
        print(f"Event ID: {event['id']}")
        print(f"Created: {event['created']}")
    except ValueError as e:
        print(f"\n=== Webhook Error: Invalid Payload ===")
        print(f"Error: {str(e)}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"\n=== Webhook Error: Invalid Signature ===")
        print(f"Error: {str(e)}")
        print(f"Webhook Secret Used: {STRIPE_WEBHOOK_SECRET[:6]}...")
        return jsonify({"error": "Invalid signature"}), 400

    # Handle different event types
    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            amount = session["amount_total"] / 100
            
            print(f"\n=== Checkout Session Completed ===")
            print(f"Session ID: {session['id']}")
            print(f"Amount: ${amount:.2f}")
            print(f"Customer Email: {session.get('customer_details', {}).get('email')}")
            print(f"Customer Name: {session.get('customer_details', {}).get('name')}")
            print(f"Payment Status: {session.get('payment_status')}")
            
            # Create or update customer in Stripe
            customer_email = session.get('customer_details', {}).get('email')
            customer_name = session.get('customer_details', {}).get('name')
            
            if customer_email:
                try:
                    # Search for existing customer
                    customers = stripe.Customer.list(email=customer_email)
                    if customers.data:
                        customer = customers.data[0]
                        # Update customer if needed
                        if customer_name and customer.name != customer_name:
                            customer = stripe.Customer.modify(
                                customer.id,
                                name=customer_name
                            )
                    else:
                        # Create new customer
                        customer = stripe.Customer.create(
                            email=customer_email,
                            name=customer_name
                        )
                    
                    print(f"Customer ID: {customer.id}")
                    
                    # Store payment details
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    payment_intent = stripe.PaymentIntent.modify(
                        payment_intent.id,
                        metadata={
                            'customer_id': customer.id,
                            'customer_email': customer_email,
                            'customer_name': customer_name,
                            'phone': session.get('metadata', {}).get('phone')
                        }
                    )
                    
                    print(f"Payment Intent updated with customer details")
                    
                except Exception as e:
                    print(f"Error handling customer: {str(e)}")
            
            # Send SMS notification
            if send_sms(amount):
                return jsonify({
                    "message": "Payment processed and SMS sent",
                    "amount": amount,
                    "phone": USER_PHONE,
                    "session_id": session['id'],
                    "customer_email": customer_email,
                    "customer_name": customer_name
                }), 200
            else:
                return jsonify({"error": "Failed to send SMS"}), 500

        else:
            print(f"\n=== Unhandled Event Type: {event['type']} ===")
            return jsonify({"message": f"Unhandled event type: {event['type']}"}), 400

    except Exception as e:
        print(f"\n=== Error Processing Event ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        return jsonify({"error": f"Error processing event: {str(e)}"}), 500

    return jsonify({"status": "success"}), 200

@app.route("/success")
def success():
    # Get payment information from session or query parameters
    payment_status = request.args.get('payment_status', 'completed')
    amount = request.args.get('amount', '50.00')
    transaction_id = request.args.get('transaction_id', '')
    
    # If this is a direct access to success page without payment, redirect to home
    if not transaction_id or transaction_id == '{CHECKOUT_SESSION_ID}':
        return redirect('/')
    
    return render_template("success.html", 
                         payment_status=payment_status,
                         amount=amount,
                         transaction_id=transaction_id)

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    # Verify environment variables are set
    required_env_vars = {
        "STRIPE_API_KEY": stripe.api_key,
        "STRIPE_PUBLIC_KEY": STRIPE_PUBLIC_KEY,
        "STRIPE_WEBHOOK_SECRET": STRIPE_WEBHOOK_SECRET,
        "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
        "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN,
        "TWILIO_PHONE_NUMBER": TWILIO_PHONE_NUMBER,
        "USER_PHONE": USER_PHONE
    }
    
    missing_vars = [var for var, value in required_env_vars.items() if not value]
    if missing_vars:
        print("\n=== Missing Required Environment Variables ===")
        for var in missing_vars:
            print(f"- {var}")
        exit(1)
    
    print("\n=== Starting Flask Server ===")
    print("Configuration:")
    print(f"- Twilio Account: {TWILIO_ACCOUNT_SID[:6]}...{TWILIO_ACCOUNT_SID[-4:]}")
    print(f"- Twilio Phone: {TWILIO_PHONE_NUMBER}")
    print(f"- User Phone: {USER_PHONE}")
    print(f"- Stripe Webhook Secret: {STRIPE_WEBHOOK_SECRET[:6]}...")
    app.run(debug=True, port=5000)