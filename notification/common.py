from abc import ABCMeta, abstractmethod


class NotificationFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, data): pass


class Notification(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, body):
        self.body = body


class NotificationSender(object):
    __metaclass__ = ABCMeta

    def send(self, notification): pass