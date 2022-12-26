from abc import ABCMeta, abstractmethod


class BotInterface(metaclass=ABCMeta):
    bots_created = {}
    @abstractmethod
    def __init__(self, tf, pair):
        self.tf = tf
        self.pair = pair

    @abstractmethod
    def entry(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def update(self):
        pass
