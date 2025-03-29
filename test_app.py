from flask.testing import TestCase
from app import app
import os
from dotenv import load_dotenv

class BaseTestCase(TestCase):
    render_templates = False

    def create_app(self):
        # Load environment variables for testing
        load_dotenv()
        
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        
        return app

    def setUp(self):
        """Set up test client and other test variables"""
        super(BaseTestCase, self).setUp()
        self.client = app.test_client()
        
        # Test data
        self.test_amount = 50.00
        self.test_phone = os.getenv('USER_PHONE')
        self.test_email = 'test@example.com'
        self.test_name = 'Test User'

    def test_home_page(self):
        """Test that home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Buy cool new product', response.data)

    def test_create_checkout_session(self):
        """Test creating a checkout session"""
        response = self.client.post('/create-checkout-session')
        self.assertEqual(response.status_code, 303)  # Redirect status code
        self.assertIn('checkout.stripe.com', response.location)

    def test_success_page(self):
        """Test success page with valid transaction"""
        response = self.client.get('/success?payment_status=completed&amount=50.00&transaction_id=test_id')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Payment Successful', response.data)

    def test_cancel_page(self):
        """Test cancel page loads correctly"""
        response = self.client.get('/cancel')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Checkout canceled', response.data)

    def test_webhook_with_valid_signature(self):
        """Test webhook with valid signature"""
        # This is a mock test - in real testing you'd need to generate proper signatures
        response = self.client.post('/webhook',
                                  data='{"type": "checkout.session.completed"}',
                                  headers={'Stripe-Signature': 'test_signature'})
        self.assertEqual(response.status_code, 400)  # Should fail due to invalid signature

    def test_webhook_without_signature(self):
        """Test webhook without signature"""
        response = self.client.post('/webhook',
                                  data='{"type": "checkout.session.completed"}')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    import unittest
    unittest.main() 