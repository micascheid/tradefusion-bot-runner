from BotInterface import BotInterface


class CSP(BotInterface):
    def __init__(self, name, tf, pair):
        super().__init__(name, tf, pair)


    def entry_exit(self):
        pass

    def trade_history_build(self, exit_info):
        pass

    def strategy_indicators(self):
        pass

    def entry(self, entry_info):
        print("CSP is looking for entry on {},  on the {} timeframe".format(self.pair, self.tf))

    def exit(self, exit_info):
        pass

    def update(self, subscribee):
        print(f"{self.name} Looking for entry on {self.tf} for the {self.pair} trading pair: \n      {subscribee.data}")