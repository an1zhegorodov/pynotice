import sys
sys.path.insert(0, "../")
import os
from flask import Flask, request
from jinja2 import Template
from notification import slack


app = Flask(__name__)

@app.route("/bitbucket_to_slack", methods=["POST"])
def slack_webhook():
    data = request.json
    data["event"] = request.headers["X-Event-Key"]

    notification = notification_factory.create(data)
    return sender.send(notification)

def get_templates():
    template = ("`{{ actor_display_name }}` has just %s `{{ source_branch }} -> {{ destination_branch }}`"
                " <{{ pull_request_link }}|pull request> at `{{ repository_full_name }}`")
    comment_template = "%s \n>>> {{ comment_text }}" % template
    comment_link_template = "%s a <{{ comment_link }}|comment> to"

    templates = {
        "pullrequest:created": Template(template % "created"),
        "pullrequest:updated": Template(template % "updated"),
        "pullrequest:approved": Template(template % "approved"),
        "pullrequest:unapproved": Template(template % "unapproved"),
        "pullrequest:fulfilled": Template(template % "merged"),
        "pullrequest:rejected": Template(template % "rejected"),
        "pullrequest:comment_created": Template(comment_template % comment_link_template % "created"),
        "pullrequest:comment_updated": Template(comment_template % comment_link_template % "updated"),
        "pullrequest:comment_deleted": Template(comment_template % comment_link_template % "deleted"),
    }

    return templates

def get_icons():
    return {
        "pullrequest:created": ":man_with_turban:",
        "pullrequest:updated": ":man_with_turban:",
        "pullrequest:approved": ":beers:",
        "pullrequest:unapproved": ":ambulance:",
        "pullrequest:fulfilled": ":octocat:",
        "pullrequest:rejected": ":shit:",
        "pullrequest:comment_created": ":microscope:",
        "pullrequest:comment_updated": ":microscope:",
        "pullrequest:comment_deleted": ":speak_no_evil:"
    }

if __name__ == "__main__":
    SLACK_CHANNEL = os.environ["PYNOTICE_SLACK_CHANNEL"]
    SLACK_URL = os.environ["PYNOTICE_SLACK_URL"]
    icons = get_icons()
    templates = get_templates()
    notification_factory = slack.BitbucketNotificationFactory(templates, icons)
    sender = slack.NotificationSender(SLACK_URL, SLACK_CHANNEL)
    port = int(os.environ.get("PORT", os.environ["PYNOTICE_PORT"]))
    app.run(host=os.environ["PYNOTICE_HOST"], port=port)