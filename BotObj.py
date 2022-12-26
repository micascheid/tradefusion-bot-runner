

class BotObj:
    # instances = {}
    #
    # def __new__(cls, name, tf, pair):
    #     try:
    #         return cls.instances[name, tf, pair]
    #     except KeyError:
    #         pass
    #     obj = super().__new__(cls)
    #
    #     cls.instances[val] = obj
    #
    #     return obj
    def __init__(self, name, tf, pair):
        self.name = name
        self.tf = tf
        self.pair = pair

    def get_name(self):
        return self.name

    def get_tf(self):
        return self.tf

    def get_pair(self):
        return self.pair

    def __str__(self):
        return f"BotName: {self.get_name()}, Timeframe: {self.get_tf()}, Pair: {self.get_pair()}"
