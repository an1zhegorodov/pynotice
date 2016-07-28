import urllib2
import json
from notification import common


class NotificationFactory(common.NotificationFactory):
    def create(self, data):
        return Notification(data)


class BitbucketNotificationFactory(common.NotificationFactory):
    def __init__(self, templates, icons):
        self.icons = icons
        self.templates = templates

    def create(self, data):
        event = data["event"]
        template_data = {
            "pull_request_link": data["pullrequest"]["links"]["html"]["href"],
            "actor_display_name": data["actor"]["display_name"],
            "source_branch": data["pullrequest"]["source"]["branch"]["name"],
            "destination_branch": data["pullrequest"]["destination"]["branch"]["name"],
            "repository_full_name": data["repository"]["full_name"]
        }

        comment_data = self.get_comment_data(data)
        if comment_data:
            template_data.update(comment_data)

        notification_body = {
            "icon_emoji": self.get_icon(event),
            "text": self.get_template(event).render(template_data),
            "username": "Bitbucket"
        }

        return Notification(notification_body)

    def get_template(self, event):
        return self.templates[event]

    def get_icon(self, event):
        return self.icons[event]

    def get_comment_data(self, data):
        try:
            comment_data = {
                "comment_text": data["comment"]["content"]["raw"],
                "comment_link": data["comment"]["links"]["html"]["href"]
            }

            return comment_data
        except KeyError:
            return False


class Notification(common.Notification):
    def __init__(self, body):
        super(Notification, self).__init__(body)

    def set_channel(self, channel):
        self.body["channel"] = channel

    def __str__(self):
        return json.dumps(self.body)


class NotificationSender(common.NotificationSender):
    def __init__(self, url, channel):
        self.channel = channel
        self.url = url

    def send(self, notification):
        notification.set_channel(self.channel)
        request = urllib2.Request(self.url, str(notification))
        response = urllib2.urlopen(request)

        return response.read()