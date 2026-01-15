import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


class PostmarkEmailSender:
    SMTP_SERVER = "smtp.postmarkapp.com"
    SMTP_PORT = 587

    def __init__(self):
        load_dotenv()
        api_token = os.getenv("POSTMARK_API_TOKEN")
        sender_email = os.getenv("SENDER_EMAIL")
        if api_token is None:
            raise ValueError("POSTMARK_API_TOKEN not found in environment variables")
        self.api_token = api_token
        if sender_email is None:
            raise ValueError("SENDER_EMAIL not found in environment variables")
        self.sender_email = sender_email

    def check_credentials(self, test_connection: bool = True) -> dict:
        """Check if Postmark credentials are set and optionally test if they're usable.
        
        Args:
            test_connection: If True, attempts to connect to SMTP server to validate credentials.
                           If False, only checks if credentials are present.
        
        Returns:
            A dictionary with the following keys:
                - credentials_set (bool): Whether both API token and sender email are present
                - api_token_set (bool): Whether POSTMARK_API_TOKEN is set
                - sender_email_set (bool): Whether SENDER_EMAIL is set
                - connection_valid (bool or None): Whether connection to SMTP server succeeded.
                                                   None if test_connection is False.
                - error (str or None): Error message if connection test failed
        """
        result = {
            "api_token_set": self.api_token is not None and self.api_token != "",
            "sender_email_set": self.sender_email is not None and self.sender_email != "",
            "connection_valid": None,
            "error": None
        }
        result["credentials_set"] = result["api_token_set"] and result["sender_email_set"]
        
        if test_connection and result["credentials_set"]:
            try:
                with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT, timeout=10) as server:
                    server.starttls()
                    server.login(self.api_token, self.api_token)
                    result["connection_valid"] = True
            except Exception as e:
                result["connection_valid"] = False
                result["error"] = str(e)
        
        return result

    def send_email(self, to_email: str, subject: str, body: str):
        """Send an email using Postmark SMTP server."""
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()  # Enable TLS
                server.login(
                    self.api_token, self.api_token
                )  # Using API token as both username and password
                server.send_message(msg)
                return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
