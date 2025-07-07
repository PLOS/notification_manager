from plugins.notification_manager import views
from django.urls import re_path

urlpatterns = [
    re_path(r"^manager/$", views.manager, name="notification_manager_manager"),
]
