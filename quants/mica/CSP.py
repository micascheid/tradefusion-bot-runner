from BotInterface import BotInterface


class CSP(BotInterface):
    def __init__(self, tf, pair):
        super().__init__(tf, pair)
        BotInterface.bots_created[tf+pair] = self

    def entry(self):
        print("CSP is looking for entry on {},  on the {} timeframe".format(self.pair, self.tf))

    def exit(self):
        pass

    def update(self):
        pass