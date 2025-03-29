import unittest
from flask.testing import TestCase
from app import app
import os
from dotenv import load_dotenv

class ViewsTests(TestCase):
    def create_app(self):
        # Load environment variables for testing
        load_dotenv()
        
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        return app

    def setUp(self):
        """Set up test client and other test variables"""
        super(ViewsTests, self).setUp()
        self.client = app.test_client()

    def test_get_to_home_route_should_render_default_view(self):
        """Test home route renders home template"""
        response = self.client.get('/')
        self.assert_template_used('home.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_checkout_route_should_render_checkout_view(self):
        """Test checkout route renders checkout template"""
        response = self.client.get('/checkout')
        self.assert_template_used('checkout.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_success_route_should_render_success_view(self):
        """Test success route renders success template"""
        response = self.client.get('/success')
        self.assert_template_used('success.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_cancel_route_should_render_cancel_view(self):
        """Test cancel route renders cancel template"""
        response = self.client.get('/cancel')
        self.assert_template_used('cancel.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_webhook_route_should_return_200(self):
        """Test webhook route returns 200 status code"""
        response = self.client.get('/webhook')
        self.assertEqual(response.status_code, 200)

    def test_post_to_webhook_route_with_valid_data(self):
        """Test webhook route handles POST requests"""
        test_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_email': 'test@example.com',
                    'amount_total': 5000
                }
            }
        }
        response = self.client.post('/webhook', json=test_data)
        self.assertEqual(response.status_code, 200)

    def test_get_to_checkout_with_session_id(self):
        """Test checkout route with session ID"""
        session_id = 'test_session_123'
        response = self.client.get(f'/checkout?session_id={session_id}')
        self.assert_template_used('checkout.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_success_with_session_id(self):
        """Test success route with session ID"""
        session_id = 'test_session_123'
        response = self.client.get(f'/success?session_id={session_id}')
        self.assert_template_used('success.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_cancel_with_session_id(self):
        """Test cancel route with session ID"""
        session_id = 'test_session_123'
        response = self.client.get(f'/cancel?session_id={session_id}')
        self.assert_template_used('cancel.html')
        self.assertEqual(response.status_code, 200)

    def test_get_to_nonexistent_route_should_return_404(self):
        """Test nonexistent route returns 404"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_post_to_checkout_route_should_create_session(self):
        """Test checkout route creates Stripe session"""
        test_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'amount': 50.00
        }
        response = self.client.post('/checkout', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('checkout.html')

    def test_get_to_success_with_invalid_session_id(self):
        """Test success route with invalid session ID"""
        session_id = 'invalid_session'
        response = self.client.get(f'/success?session_id={session_id}')
        self.assertEqual(response.status_code, 400)

    def test_get_to_cancel_with_invalid_session_id(self):
        """Test cancel route with invalid session ID"""
        session_id = 'invalid_session'
        response = self.client.get(f'/cancel?session_id={session_id}')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main() 