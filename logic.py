import json

import requests
from django.contrib import messages
from plugins.notification_manager.models import NotificationMessage
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)

def send_message(request, body):
    """
    Sends a message with the given body.
    :param request: The request when sending the event.
    :param body: the body of the message to send.
    """

    # get the per-journal settings for the plugin
    (
        notification_manager_enabled,
        notification_manager_email,
        notification_manager_password,
        notification_manager_url,
        notification_manager_authorization_url,
    ) = get_plugin_settings(request.journal)

    message = NotificationMessage()

    # setup switchboard option
    url_to_use = notification_manager_url
    if not url_to_use.endswith("/"):
        url_to_use += "/"

    # try authorization
    token, success = authorize(notification_manager_email, notification_manager_password, notification_manager_authorization_url)
    if not success:
        message.authorized = False
        message.save()
        messages.add_message(
            request,
            messages.ERROR,
            "Failed to authorize.",
        )
        return

    message.authorized = True

    payload = build_payload(body)

    # send the payload
    json_output, success = send_payload(payload, token, url_to_use)

    message.message = payload
    message.response = json_output

    if success:
        message.success = True
        message.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            "Message sent.",
        )
        return

    message.success = False
    message.save()

    messages.add_message(
        request,
        messages.ERROR,
        f"Failed to send the message: \
        {[item for item in json_output.get('errorMessage', [])]}",
    )

def authorize(email, password, url_to_use):
    """
    Obtain a bearer token from the authorization service.
    :param email: the email to use
    :param password: the password to use
    :param url_to_use: the base URL to use
    :return:
    """
    auth_url = f"{url_to_use}authorize"
    authorization_json = build_authorization_json(email, password)

    r = requests.post(
        f"{url_to_use}authorize",
        data=json.dumps(authorization_json),
        timeout=30,
    )

    if r.status_code != 200:
        logger.error(
            f"Failed to authorize with the given URL: {auth_url}: "
            f"{r.status_code}"
        )
        return None, False

    authorization_response = r.json()

    if "error" in authorization_response:
        logger.error(
            f"Failed to authorize: {auth_url}: "
            f"{authorization_response['errorMessage']}"
        )

        return None, False

    # get the token
    if "token" not in authorization_response:
        logger.error(
            f"Failed to authorize: {auth_url}: "
            "no token returned"
        )
        return None, False

    token = authorization_response.get("token", None)

    return token, True

def build_authorization_json(email, password):
    """
    Build the authorization JSON
    :param email: the email to use
    :param password: the password to use
    """
    return {
        "email": email,
        "password": password,
    }

def send_payload(payload, token, url_to_use):
    """
    Send the payload to the Notification Service.
    :param payload: the payload to send
    :param token: the bearer token to use
    :param url_to_use: the base URL to use
    """
    headers = {"Authorization": "Bearer " + token}
    message_url = f"{url_to_use}message"

    r = requests.post(
        message_url, headers=headers, data=json.dumps(payload), timeout=30
    )

    try:
        json_output = r.json()
    except Exception:
        json_output = {"message": r.content}

    is_errored = json_output.get("error", False)

    if is_errored:
        return json_output, False

    return json_output, True

def build_payload(body):
    """
    Build the payload to send.
    :param body: The body of the payload.
    """
    return {
        "header": build_header(),
        "data": body,
    }

def build_header():
    """
    Build the header for the payload.
    """
    return {

    }

def get_plugin_settings(journal):
    """
    Get the plugin settings for the Notification Manager.
    :param journal: the journal
    """
    notification_manager_enabled = setting_handler.get_setting(
        "plugin:notification_manager_plugin", "notification_manager_send", journal
    )
    notification_manager_email = setting_handler.get_setting(
        "plugin:notification_manager_plugin", "notification_manager_email", journal
    )
    notification_manager_password = setting_handler.get_setting(
        "plugin:notification_manager_plugin", "notification_manager_password", journal
    )
    notification_manager_url = setting_handler.get_setting(
        "plugin:notification_manager_plugin", "notification_manager_url", journal
    )
    notification_manager_authorization_url = setting_handler.get_setting(
        "plugin:notification_manager_plugin", "notification_manager_authorization_url", journal
    )

    return (
        notification_manager_enabled,
        notification_manager_email,
        notification_manager_password,
        notification_manager_url,
        notification_manager_authorization_url,
    )

def save_plugin_settings(
        notification_manager_enabled,
        notification_manager_email,
        notification_manager_password,
        notification_manager_url,
        notification_manager_authorization_url,
        request,
):
    """
    Save the plugin settings for the notification manager plugin
    :param notification_manager_email: the email
    :param notification_manager_enabled: whether the plugin is enabled
    :param notification_manager_password: the password
    :param notification_manager_authorization_url: the authentication URL
    :param notification_manager_url: the live URL
    :param request: the request object (to specify the journal)
    """
    setting_handler.save_setting(
        setting_group_name="plugin:notification_manager_plugin",
        setting_name="notification_manager_send",
        journal=request.journal,
        value=notification_manager_enabled,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:notification_manager_plugin",
        setting_name="notification_manager_email",
        journal=request.journal,
        value=notification_manager_email,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:notification_manager_plugin",
        setting_name="notification_manager_password",
        journal=request.journal,
        value=notification_manager_password,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:notification_manager_plugin",
        setting_name="notification_manager_url",
        journal=request.journal,
        value=notification_manager_url,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:notification_manager_plugin",
        setting_name="notification_manager_authorization_url",
        journal=request.journal,
        value=notification_manager_authorization_url,
    )