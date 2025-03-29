import unittest
from flask.testing import TestCase
from app import app
import os
from dotenv import load_dotenv
from flask import redirect, url_for, render_template

def redirect_to(endpoint, **kwargs):
    """Helper function to redirect to a specific endpoint"""
    return redirect(url_for(endpoint, **kwargs))

def view(template, **kwargs):
    """Helper function to render a template"""
    return render_template(f"{template}.html", **kwargs)

class ViewHelperTests(TestCase):
    def create_app(self):
        # Load environment variables for testing
        load_dotenv()
        
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        return app

    def setUp(self):
        """Set up test client and other test variables"""
        super(ViewHelperTests, self).setUp()
        self.client = app.test_client()

    def test_redirect_to_home_redirects_to_same_location(self):
        """Test redirect_to helper redirects to home page"""
        assert redirect_to('home').location == redirect(url_for('home')).location

    def test_redirect_to_success_redirects_to_same_location(self):
        """Test redirect_to helper redirects to success page"""
        assert redirect_to('success').location == redirect(url_for('success')).location

    def test_redirect_to_cancel_redirects_to_same_location(self):
        """Test redirect_to helper redirects to cancel page"""
        assert redirect_to('cancel').location == redirect(url_for('cancel')).location

    def test_redirect_to_with_parameters_redirects_to_same_location(self):
        """Test redirect_to helper with URL parameters"""
        session_id = 'test_session_123'
        assert redirect_to('success', session_id=session_id).location == \
               redirect(url_for('success', session_id=session_id)).location

    def test_view_home_renders_same_template(self):
        """Test view helper renders home template"""
        assert view('home') == render_template('home.html')

    def test_view_success_renders_same_template(self):
        """Test view helper renders success template"""
        assert view('success') == render_template('success.html')

    def test_view_cancel_renders_same_template(self):
        """Test view helper renders cancel template"""
        assert view('cancel') == render_template('cancel.html')

    def test_view_with_context_renders_same_template(self):
        """Test view helper renders template with context variables"""
        context = {'message': 'Payment successful'}
        assert view('success', **context) == render_template('success.html', **context)

    def test_view_with_multiple_context_variables(self):
        """Test view helper renders template with multiple context variables"""
        context = {
            'message': 'Payment successful',
            'amount': 50.00,
            'email': 'test@example.com'
        }
        assert view('success', **context) == render_template('success.html', **context)

    def test_redirect_to_with_query_parameters(self):
        """Test redirect_to helper with query parameters"""
        params = {'status': 'success', 'session_id': 'test_123'}
        assert redirect_to('success', **params).location == \
               redirect(url_for('success', **params)).location

    def test_view_with_template_inheritance(self):
        """Test view helper with template inheritance"""
        base_context = {'title': 'Payment Success'}
        assert view('success', **base_context) == render_template('success.html', **base_context)

if __name__ == '__main__':
    unittest.main() 