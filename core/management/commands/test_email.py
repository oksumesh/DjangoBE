from django.core.management.base import BaseCommand
from core.email_service import EmailService

class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='officialsumesh07@gmail.com',
            help='Email address to send test email to'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Test User',
            help='Name for the test email'
        )

    def handle(self, *args, **options):
        email = options['email']
        name = options['name']
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing email functionality for {email}')
        )
        
        # Test OTP email
        self.stdout.write('Sending OTP email...')
        otp_result = EmailService.send_otp_email(email, '123456', name)
        
        if otp_result:
            self.stdout.write(
                self.style.SUCCESS('✅ OTP email sent successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Failed to send OTP email')
            )
        
        # Test confirmation email
        self.stdout.write('Sending confirmation email...')
        confirm_result = EmailService.send_password_reset_confirmation(email, name)
        
        if confirm_result:
            self.stdout.write(
                self.style.SUCCESS('✅ Confirmation email sent successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Failed to send confirmation email')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Email testing completed! Check your inbox.')
        )
