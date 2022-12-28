from abc import ABCMeta, abstractmethod


class BotInterface(metaclass=ABCMeta):
    bots_created = {}
    @abstractmethod
    def __init__(self, name, tf, pair):
        self.name = name
        self.tf = tf
        self.pair = pair
        BotInterface.bots_created[name, tf + pair] = self

    def get_tf(self):
        return self.tf

    def get_pair(self):
        return self.pair

    @abstractmethod
    def entry(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def update(self, subscribee):
        pass
