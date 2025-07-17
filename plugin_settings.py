from utils import plugins
from utils.install import update_settings

PLUGIN_NAME = 'Notification Manager'
DISPLAY_NAME = 'Notification Manager'
DESCRIPTION = 'Manages events to third party APIs.'
AUTHOR = 'PLOS'
VERSION = '0.1'
SHORT_NAME = 'notification_manager'
MANAGER_URL = 'notification_manager_manager'
JANEWAY_VERSION = "1.7.4"



class NotificationManagerPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION
    


def install():
    NotificationManagerPlugin.install()
    update_settings(
        file_path='plugins/notification_manager/install/settings.json'
    )


def hook_registry():
    NotificationManagerPlugin.hook_registry()


def register_for_events():
    # Plugin modules can't be imported until plugin is loaded
    from events import logic as events_logic
    events_logic.Events.register_for_event(
        events_logic.Events.ON_ARTICLE_SUBMITTED, # The event to be registered for
        publication_event, # The function to be called
    )
    pass

def publication_event(**kwargs):
    # note that import must be here to avoid circular imports
    from plugins.notification_manager import logic

    request = kwargs.get('request')
    article = kwargs.get('article')
    # do something here

    body = {
        "data": [
            {
                "document_type": "article",
                "id": article.id,
            },
        ],
    }

    logic.send_message(request, body)


