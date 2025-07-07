"""
Models for the plugin.
"""

from django.db import models


class NotificationMessage(models.Model):
    """
    A message that has been sent the notification service.
    """
    authorized = models.BooleanField(default=False)

    message = models.TextField()
    response = models.TextField()

    message_date_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)