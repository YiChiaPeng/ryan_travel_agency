from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.utils.smtp import get_smtp_server

class NotificationService:
    def __init__(self):
        self.smtp_server = get_smtp_server()

    def send_email(self, recipient_email, subject, body):
        message = MIMEMultipart()
        message['From'] = self.smtp_server['sender_email']
        message['To'] = recipient_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        try:
            with SMTP(self.smtp_server['host'], self.smtp_server['port']) as server:
                server.starttls()
                server.login(self.smtp_server['sender_email'], self.smtp_server['password'])
                server.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def notify_b2b_client(self, client_email, notification_message):
        subject = "Notification from B2B Document Management System"
        body = f"Dear B2B Client,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        return self.send_email(client_email, subject, body)

    def notify_admin(self, admin_email, notification_message):
        subject = "Admin Notification from B2B Document Management System"
        body = f"Dear Admin,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        return self.send_email(admin_email, subject, body)