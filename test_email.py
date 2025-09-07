#!/usr/bin/env python
"""
Test script for email functionality
Run this script to test if email sending is working properly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/sumesh/Documents/Projects/Red/RedCurtainsWebBackend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviepoll.settings')
django.setup()

from core.email_service import EmailService

def test_otp_email():
    """Test sending OTP email"""
    print("Testing OTP email sending...")
    
    # Test email (replace with your email for testing)
    test_email = "officialsumesh07@gmail.com"
    test_otp = "123456"
    test_name = "Sumesh Kumar"
    
    try:
        result = EmailService.send_otp_email(test_email, test_otp, test_name)
        if result:
            print(f"✅ OTP email sent successfully to {test_email}")
            print(f"Check your email for the OTP: {test_otp}")
        else:
            print("❌ Failed to send OTP email")
    except Exception as e:
        print(f"❌ Error sending OTP email: {str(e)}")

def test_confirmation_email():
    """Test sending password reset confirmation email"""
    print("\nTesting password reset confirmation email...")
    
    test_email = "officialsumesh07@gmail.com"
    test_name = "Sumesh Kumar"
    
    try:
        result = EmailService.send_password_reset_confirmation(test_email, test_name)
        if result:
            print(f"✅ Confirmation email sent successfully to {test_email}")
        else:
            print("❌ Failed to send confirmation email")
    except Exception as e:
        print(f"❌ Error sending confirmation email: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Red Curtain Email Service")
    print("=" * 50)
    
    test_otp_email()
    test_confirmation_email()
    
    print("\n" + "=" * 50)
    print("✅ Email testing completed!")
    print("Check your email inbox for the test emails.")
