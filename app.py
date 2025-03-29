import stripe
from flask import Flask, render_template, request, jsonify
from twilio.rest import Client
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Stripe API Key
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_PHONE = "+919042444246"  # You might want to store this in your database for real applications

# Load Stripe webhook secret
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

def send_sms(amount=50.00):
    """Function to send SMS using Twilio"""
    try:
        # Verify Twilio credentials
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise ValueError("Twilio credentials are missing")
            
        print("\n=== Twilio Configuration ===")
        print(f"Account SID: {TWILIO_ACCOUNT_SID[:6]}...{TWILIO_ACCOUNT_SID[-4:]}")
        print(f"Auth Token: {TWILIO_AUTH_TOKEN[:6]}...{TWILIO_AUTH_TOKEN[-4:]}")
        print(f"From Number: {TWILIO_PHONE_NUMBER}")
        print(f"To Number: {USER_PHONE}")
        
        # Create Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Format phone numbers
        if not USER_PHONE.startswith('+'):
            USER_PHONE = '+' + USER_PHONE
        if not USER_PHONE.startswith('+91'):
            USER_PHONE = '+91' + USER_PHONE.lstrip('+')
            
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
    return render_template("index.html", key=os.getenv("STRIPE_PUBLIC_KEY"))

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
            success_url=request.host_url + "success",
            cancel_url=request.host_url + "cancel",
            metadata={"phone": USER_PHONE}  # Store phone number in metadata
        )
        return jsonify({"id": session.id})
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
            WEBHOOK_SECRET
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
        return jsonify({"error": "Invalid signature"}), 400

    # Handle different event types
    try:
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            print("\n=== Payment Intent Succeeded ===")
            print(f"Payment Intent ID: {payment_intent['id']}")
            print(f"Amount: ${payment_intent['amount']/100:.2f}")
            print(f"Status: {payment_intent['status']}")
            
            # Send SMS notification for successful payment
            if send_sms(payment_intent['amount']/100):
                return jsonify({
                    "message": "Payment processed and SMS sent",
                    "payment_intent_id": payment_intent['id'],
                    "amount": payment_intent['amount']/100
                }), 200
            else:
                return jsonify({"error": "Failed to send SMS"}), 500

        elif event["type"] == "payment_method.attached":
            payment_method = event["data"]["object"]
            print("\n=== Payment Method Attached ===")
            print(f"Payment Method ID: {payment_method['id']}")
            print(f"Type: {payment_method['type']}")
            return jsonify({"message": "Payment method attached"}), 200

        elif event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            amount = session["amount_total"] / 100
            
            print(f"\n=== Checkout Session Completed ===")
            print(f"Session ID: {session['id']}")
            print(f"Amount: ${amount:.2f}")
            print(f"Customer Phone: {USER_PHONE}")
            print(f"Payment Status: {session.get('payment_status')}")
            
            # Send SMS notification
            if send_sms(amount):
                return jsonify({
                    "message": "Payment processed and SMS sent",
                    "amount": amount,
                    "phone": USER_PHONE,
                    "session_id": session['id']
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
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    # Verify environment variables are set
    required_env_vars = [
        "STRIPE_API_KEY",
        "STRIPE_PUBLIC_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
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
    print(f"- Stripe Webhook Secret: {WEBHOOK_SECRET[:6]}...")
    app.run(debug=True, port=5000)