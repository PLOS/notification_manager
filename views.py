from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from plugins.notification_manager import forms
from security import decorators

from plugins.notification_manager.logic import get_plugin_settings, save_plugin_settings


@staff_member_required
@decorators.has_journal
def manager(request):
    """
    The manager view for the Notification Manager plugin.
    :param request: the request object
    """
    (
        notification_manager_enabled,
        notification_manager_email,
        notification_manager_password,
        notification_manager_url,
        notification_manager_authorization_url,
    ) = get_plugin_settings(request.journal)

    if request.POST:
        form = forms.NotificationManagerForm(request.POST)

        if form.is_valid():
            notification_manager_enabled = form.cleaned_data["enabled"]
            notification_manager_email = form.cleaned_data["email"]
            notification_manager_password = form.cleaned_data["password"]
            notification_manager_url = form.cleaned_data["url"]
            notification_manager_authorization_url = form.cleaned_data["authentication_url"]

            save_plugin_settings(
                notification_manager_enabled,
                notification_manager_email,
                notification_manager_password,
                notification_manager_url,
                notification_manager_authorization_url,
                request,
            )

    else:
        form = forms.NotificationManagerForm(
            initial={
                "enabled": notification_manager_enabled,
                "email": notification_manager_email,
                "password": notification_manager_password,
                "url": notification_manager_url,
                "authentication_url": notification_manager_authorization_url,
            }
        )

    template = "notification_manager/manager.html"
    context = {
        "form": form,
    }

    return render(request, template, context)
