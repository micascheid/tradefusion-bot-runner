from BotInterface import BotInterface


class KrownCross(BotInterface):
    krowncross_dict = {}

    def __init__(self, name, tf, pair):
        super().__init__(name, tf, pair)
        print("Being Created")
        # BotInterface.bots_created[tf+pair] = self

    def entry(self):
        print("Krown Cross is looking for entry on {},  on the {} timeframe".format(self.pair, self.tf))

    def exit(self):
        print("Krown Cross is looking for exit on {}".format(self.tf))

    def update(self, subscribee):
        print(f"{self.name} Looking for entry on {self.tf} for the {self.pair} trading pair: \n      {subscribee.data}")