from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        EMERGENCY = "EMERGENCY", "Emergency Request"
        REWARD = "REWARD", "Reward / Badge"
        CAMP = "CAMP", "Donation Camp"
        SYSTEM = "SYSTEM", "System"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name="notifications")
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=12, choices=Type.choices,
                                         default=Type.SYSTEM)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.recipient.username}"


def notify(recipient, title, message, notification_type=Notification.Type.SYSTEM, link=""):
    """Helper to create a notification."""
    return Notification.objects.create(
        recipient=recipient, title=title, message=message,
        notification_type=notification_type, link=link,
    )
