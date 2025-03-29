# Stripe Payment with SMS Notification

A Flask application that processes payments using Stripe and sends SMS notifications using Twilio.

## Features

- Stripe payment integration
- SMS notifications for successful payments
- Webhook handling for payment events
- Secure environment variable management

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Yaminianitha19/Stripe_Flask_.git
cd Stripe_Flask_
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Stripe and Twilio credentials in `.env`

5. Run the application:
```bash
python app.py
```

## Environment Variables

Create a `.env` file with the following variables:

- `STRIPE_API_KEY`: Your Stripe secret key
- `STRIPE_PUBLIC_KEY`: Your Stripe publishable key
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook signing secret
- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio auth token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number
- `USER_PHONE`: Recipient phone number for SMS notifications

## Testing

1. Run the test script to verify Twilio SMS:
```bash
python test_twilio.py
```

2. Test the payment flow:
   - Visit http://localhost:5000
   - Click "Pay $50.00"
   - Use Stripe test card: 4242 4242 4242 4242
   - Complete the payment
   - You should receive an SMS notification

## Security Notes

- Never commit your `.env` file or expose sensitive credentials
- Keep your API keys and secrets secure
- Use environment variables for all sensitive data

## License

MIT License
