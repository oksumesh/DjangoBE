import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomSMTPEmailBackend(EmailBackend):
    """
    Custom SMTP email backend that handles SSL certificate issues
    """
    
    def open(self):
        """
        Ensure an open connection to the email server.
        Return whether or not a new connection was required (True or False)
        or raise an exception.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        
        try:
            # Create SSL context that doesn't verify certificates
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            if self.use_ssl:
                # Use SSL
                self.connection = smtplib.SMTP_SSL(
                    self.host, 
                    self.port, 
                    timeout=self.timeout,
                    context=context
                )
            elif self.use_tls:
                # Use TLS
                self.connection = smtplib.SMTP(
                    self.host, 
                    self.port, 
                    timeout=self.timeout
                )
                self.connection.starttls(context=context)
            else:
                # Plain connection
                self.connection = smtplib.SMTP(
                    self.host, 
                    self.port, 
                    timeout=self.timeout
                )
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to open SMTP connection: {str(e)}")
            # Try fallback connection without SSL/TLS
            try:
                logger.info("Trying fallback connection without SSL/TLS...")
                self.connection = smtplib.SMTP(
                    self.host, 
                    self.port, 
                    timeout=self.timeout
                )
                if self.username and self.password:
                    self.connection.login(self.username, self.password)
                return True
            except Exception as fallback_error:
                logger.error(f"Fallback connection also failed: {str(fallback_error)}")
                raise e
