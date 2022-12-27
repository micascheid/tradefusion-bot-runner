from BotInterface import BotInterface


class KrownCross(BotInterface):
    krowncross_dict = {}

    def __init__(self, tf, pair):
        super().__init__(tf, pair)
        BotInterface.bots_created[tf+pair] = self
        print("Being Created")

    def entry(self):
        print("Krown Cross is looking for entry on {},  on the {} timeframe".format(self.pair, self.tf))

    def exit(self):
        print("Krown Cross is looking for exit on {}".format(self.tf))

    def update(self, subscribee):
        print(f"updating on the {subscribee.name} timeframe")