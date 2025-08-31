from ..utils.smtp import get_smtp_server, send_email


class NotificationService:
    def __init__(self):
        self.smtp_server = get_smtp_server()

    def send_email(self, recipient_email, subject, body):
        # Use the utility send_email function which handles SMTP details.
        return send_email(subject, body, recipient_email)

    def notify_b2b_client(self, client_email, notification_message):
        subject = "Notification from B2B Document Management System"
        body = (
            f"Dear B2B Client,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        )
        return self.send_email(client_email, subject, body)

    def notify_admin(self, admin_email, notification_message):
        subject = "Admin Notification from B2B Document Management System"
        body = (
            f"Dear Admin,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        )
        return self.send_email(admin_email, subject, body)


__all__ = ["NotificationService"]
from ..utils.smtp import get_smtp_server, send_email


class NotificationService:
    def __init__(self):
        self.smtp_server = get_smtp_server()

    def send_email(self, recipient_email, subject, body):
        # Use the utility send_email function which handles SMTP details.
        return send_email(subject, body, recipient_email)

    def notify_b2b_client(self, client_email, notification_message):
        subject = "Notification from B2B Document Management System"
        body = (
            f"Dear B2B Client,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        )
        return self.send_email(client_email, subject, body)

    def notify_admin(self, admin_email, notification_message):
        subject = "Admin Notification from B2B Document Management System"
        body = (
            f"Dear Admin,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        )
        return self.send_email(admin_email, subject, body)


__all__ = ["NotificationService"]
from ..utils.smtp import send_email
from ..utils.smtp import send_email as send_email_util, get_smtp_server
from ..utils.smtp import send_email as send_email_util, get_smtp_server


class NotificationService:
    def __init__(self):
        self.smtp_server = get_smtp_server()

    def send_email(self, recipient_email, subject, body):
        # Use the utility send_email function which handles SMTP details.
        return send_email_util(subject, body, recipient_email)

    def notify_b2b_client(self, client_email, notification_message):
        subject = "Notification from B2B Document Management System"
        body = f"Dear B2B Client,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        return self.send_email(client_email, subject, body)

    def notify_admin(self, admin_email, notification_message):
        subject = "Admin Notification from B2B Document Management System"
        body = f"Dear Admin,\n\n{notification_message}\n\nBest regards,\nB2B Document Management Team"
        return self.send_email(admin_email, subject, body)


__all__ = [
    'NotificationService'
]