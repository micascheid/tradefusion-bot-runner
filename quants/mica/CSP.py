from BotInterface import BotInterface


class CSP(BotInterface):
    def __init__(self, name, tf, pair):
        super().__init__(name, tf, pair)
        # BotInterface.bots_created[tf+pair] = self

    def entry(self):
        print("CSP is looking for entry on {},  on the {} timeframe".format(self.pair, self.tf))

    def exit(self):
        pass

    def update(self, subscribee):
        print(f"{self.name} Looking for entry on {self.tf} for the {self.pair} trading pair: \n      {subscribee.data}")