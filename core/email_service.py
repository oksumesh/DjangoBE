from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_otp_email(email, otp, user_name=None):
        """
        Send OTP email for password reset
        
        Args:
            email (str): Recipient email address
            otp (str): 6-digit OTP code
            user_name (str, optional): User's name for personalization
        """
        try:
            # Create email content
            subject = "Red Curtain - Password Reset OTP"
            
            # HTML email template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset OTP</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        background: linear-gradient(135deg, #ff6b35, #f7931e);
                        color: white;
                        padding: 15px 30px;
                        border-radius: 25px;
                        display: inline-block;
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 20px;
                    }}
                    .otp-container {{
                        background-color: #2F0000;
                        color: white;
                        padding: 30px;
                        border-radius: 15px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .otp-code {{
                        font-size: 36px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        color: #ff6b35;
                        margin: 20px 0;
                        font-family: 'Courier New', monospace;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #ff6b35, #f7931e);
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎬 Red Curtain</div>
                        <h1>Password Reset Request</h1>
                    </div>
                    
                    <p>Hello{f' {user_name}' if user_name else ''},</p>
                    
                    <p>We received a request to reset your password for your Red Curtain account. Use the OTP code below to verify your identity:</p>
                    
                    <div class="otp-container">
                        <h2>Your Verification Code</h2>
                        <div class="otp-code">{otp}</div>
                        <p>This code will expire in 10 minutes</p>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This code is valid for 10 minutes only</li>
                            <li>Never share this code with anyone</li>
                            <li>If you didn't request this, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>If you're having trouble with the code above, you can also copy and paste it directly into the app.</p>
                    
                    <div class="footer">
                        <p>This email was sent from Red Curtain Movie Polling App</p>
                        <p>If you have any questions, please contact our support team.</p>
                        <p>&copy; 2024 Red Curtain. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_message = f"""
            Red Curtain - Password Reset OTP
            
            Hello{f' {user_name}' if user_name else ''},
            
            We received a request to reset your password for your Red Curtain account.
            
            Your verification code is: {otp}
            
            This code will expire in 10 minutes.
            
            Security Notice:
            - This code is valid for 10 minutes only
            - Never share this code with anyone
            - If you didn't request this, please ignore this email
            
            If you're having trouble, you can copy and paste the code directly into the app.
            
            This email was sent from Red Curtain Movie Polling App
            If you have any questions, please contact our support team.
            
            © 2024 Red Curtain. All rights reserved.
            """
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_confirmation(email, user_name=None):
        """
        Send confirmation email after successful password reset
        
        Args:
            email (str): Recipient email address
            user_name (str, optional): User's name for personalization
        """
        try:
            subject = "Red Curtain - Password Reset Successful"
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset Successful</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        background: linear-gradient(135deg, #ff6b35, #f7931e);
                        color: white;
                        padding: 15px 30px;
                        border-radius: 25px;
                        display: inline-block;
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 20px;
                    }}
                    .success {{
                        background-color: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 20px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎬 Red Curtain</div>
                        <h1>Password Reset Successful</h1>
                    </div>
                    
                    <p>Hello{f' {user_name}' if user_name else ''},</p>
                    
                    <div class="success">
                        <h2>✅ Your password has been successfully reset!</h2>
                        <p>You can now log in to your Red Curtain account using your new password.</p>
                    </div>
                    
                    <p>If you didn't make this change, please contact our support team immediately.</p>
                    
                    <div class="footer">
                        <p>This email was sent from Red Curtain Movie Polling App</p>
                        <p>If you have any questions, please contact our support team.</p>
                        <p>&copy; 2024 Red Curtain. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
            Red Curtain - Password Reset Successful
            
            Hello{f' {user_name}' if user_name else ''},
            
            Your password has been successfully reset!
            
            You can now log in to your Red Curtain account using your new password.
            
            If you didn't make this change, please contact our support team immediately.
            
            This email was sent from Red Curtain Movie Polling App
            If you have any questions, please contact our support team.
            
            © 2024 Red Curtain. All rights reserved.
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Password reset confirmation email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset confirmation email to {email}: {str(e)}")
            return False
