from django import forms


class NotificationManagerForm(forms.Form):
    """
    The form for the notification manager.
    """

    enabled = forms.BooleanField(
        required=False, help_text="Whether to send messages."
    )
    authentication_enabled = forms.BooleanField(
        required=False, help_text="Whether to send authenticated messages."
    )
    email = forms.CharField(required=False, help_text="The email login credential.")
    password = forms.CharField(
        required=False, help_text="The password login credential.",
    )
    url = forms.CharField(
        help_text="The URL for the live deposit.", label="URL"
    )
    authentication_url = forms.CharField(
        required=False, help_text="The URL for the authentication URL.", label="Authentication URL"
    )