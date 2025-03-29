from flask.testing import TestCase
from app import app
import os
from dotenv import load_dotenv
from wtforms import Form, StringField, DecimalField, validators

class PaymentForm(Form):
    """Form for payment details"""
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    name = StringField('Name', [validators.DataRequired()])
    amount = DecimalField('Amount', [validators.DataRequired(), validators.NumberRange(min=0.01)])

class FormTests(TestCase):
    def create_app(self):
        # Load environment variables for testing
        load_dotenv()
        
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        return app

    def setUp(self):
        """Set up test client and other test variables"""
        super(FormTests, self).setUp()
        self.client = app.test_client()

    def test_payment_form_with_missing_email_should_produce_error(self):
        """Test payment form validation with missing email"""
        form = PaymentForm(email='', name='Test User', amount=50.00)
        
        assert form.validate() is False
        assert 'Email is required' in form.email.errors

    def test_payment_form_with_bad_formed_email_should_produce_error(self):
        """Test payment form validation with invalid email format"""
        form = PaymentForm(email='invalid-email', name='Test User', amount=50.00)
        
        assert form.validate() is False
        assert 'Invalid email address' in form.email.errors

    def test_payment_form_with_missing_name_should_produce_error(self):
        """Test payment form validation with missing name"""
        form = PaymentForm(email='test@example.com', name='', amount=50.00)
        
        assert form.validate() is False
        assert 'Name is required' in form.name.errors

    def test_payment_form_with_missing_amount_should_produce_error(self):
        """Test payment form validation with missing amount"""
        form = PaymentForm(email='test@example.com', name='Test User', amount=None)
        
        assert form.validate() is False
        assert 'Amount is required' in form.amount.errors

    def test_payment_form_with_invalid_amount_should_produce_error(self):
        """Test payment form validation with invalid amount"""
        form = PaymentForm(email='test@example.com', name='Test User', amount=0)
        
        assert form.validate() is False
        assert 'Amount must be greater than 0' in form.amount.errors

    def test_payment_form_with_valid_data_should_validate(self):
        """Test payment form validation with valid data"""
        form = PaymentForm(
            email='test@example.com',
            name='Test User',
            amount=50.00
        )
        
        assert form.validate() is True
        assert not form.email.errors
        assert not form.name.errors
        assert not form.amount.errors

    def test_payment_form_with_valid_data_should_handle_decimal_amount(self):
        """Test payment form validation with decimal amount"""
        form = PaymentForm(
            email='test@example.com',
            name='Test User',
            amount=50.50
        )
        
        assert form.validate() is True
        assert form.amount.data == 50.50

    def test_payment_form_with_valid_data_should_handle_large_amount(self):
        """Test payment form validation with large amount"""
        form = PaymentForm(
            email='test@example.com',
            name='Test User',
            amount=1000.00
        )
        
        assert form.validate() is True
        assert form.amount.data == 1000.00

if __name__ == '__main__':
    import unittest
    unittest.main() 