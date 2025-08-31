import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(subject, body, to_email, attachments=None):
    from_email = os.getenv('SMTP_USER')
    from_password = os.getenv('SMTP_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.example.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachments:
        for file_path in attachments:
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(file_path)}',
                    )
                    msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Attempt to start TLS if the server supports it
            try:
                server.starttls()
            except Exception:
                pass

            # Only attempt to login if credentials are provided
            if from_email and from_password:
                try:
                    server.login(from_email, from_password)
                except Exception as e:
                    print(f"SMTP login failed: {e}")

            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def get_smtp_server():
    """Backward-compatible helper that returns SMTP settings as a dict."""
    return {
        'host': os.getenv('SMTP_SERVER', 'smtp.example.com'),
        'port': int(os.getenv('SMTP_PORT', 587)),
        'sender_email': os.getenv('SMTP_USER'),
        'password': os.getenv('SMTP_PASSWORD')
    }