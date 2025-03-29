from twilio.rest import Client
import os
from dotenv import load_dotenv

def test_twilio_sms():
    # Load environment variables
    load_dotenv()
    
    # Get Twilio credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    to_number = "+919042444246"
    
    print("\n=== Twilio Configuration ===")
    print(f"Account SID: {account_sid[:6]}...{account_sid[-4:]}")
    print(f"Auth Token: {auth_token[:6]}...{auth_token[-4:]}")
    print(f"From Number: {from_number}")
    print(f"To Number: {to_number}")
    
    try:
        # Create Twilio client
        print("\nCreating Twilio client...")
        client = Client(account_sid, auth_token)
        
        # Send test message
        print("\nAttempting to send SMS...")
        message = client.messages.create(
            from_=from_number,
            body="Test SMS from Twilio - Please verify receipt",
            to=to_number
        )
        
        print("\n=== SMS Sent Successfully ===")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"Direction: {message.direction}")
        print(f"Date Created: {message.date_created}")
        
        # Check for any error codes
        if hasattr(message, 'error_code') and message.error_code:
            print(f"\nWarning: Message has error code: {message.error_code}")
            print(f"Error message: {message.error_message}")
        
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

if __name__ == "__main__":
    print("\n=== Starting Twilio SMS Test ===")
    success = test_twilio_sms()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed. Please check the error messages above.") 