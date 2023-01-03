from abc import ABCMeta, abstractmethod
from pandas import DataFrame
from firebase_admin import db


class BotInterface(metaclass=ABCMeta):
    bots_created = {}

    @abstractmethod
    def __init__(self, name, tf, pair):
        self.name = name
        self.tf = tf
        self.pair = pair
        self.data = DataFrame()
        BotInterface.bots_created[name, tf + pair] = self
        self.long_hold = 0
        self.short_hold = 0
        self.ref_entry = db.reference(f'entry/{self.name}/{self.tf+self.pair}')
        self.ref_trade_history = db.reference(f'trade_history/{self.name}/{self.tf+self.pair}/')

    def get_tf(self):
        return self.tf

    def get_pair(self):
        return self.pair


    def entry(self, entry_info):
        """
        :description: The entry_info json object gets pushed to entry/{strategy}/tf+pair/
            Only one entry per strategy tf and pair will ever persist in the database. Once exit is found the entry
            gets removed and is stored in the trade_history node of the database
        :param entry_info: a json object that contains both the candle and strategy metrics for a found upon entry
        :return: Nothing, is a db management function
        """
        print(f'"{self.name} IS MAKING ENTRY ON {self.tf} for {self.pair}')
        self.ref_entry.set(entry_info)

    @abstractmethod
    def exit(self, exit_info):
        """
        :description: handles db management for the exit of a trade
        :param exit_info: The exit_info json object contains the entirety of a trade for a given bot which contains
            all entry and exit info of the indicators for the strategy along with the candle metrics. TODO: add in
            trade metrics
        :return: Nothing, is a db management function
        """
        pass

    @abstractmethod
    def entry_exit(self):
        """
        :description: decides when to enter/exit a trade based on the latest candle data and delegates db management
            for live trading info to self.entry() and self.exit()
        :return: Nothing
        """
        pass

    def update(self, subscribee):
        """
        :description: what allows for a bot to get the latest info on the tf and pair for a data monitor in which it
            is subscribed to. Once new data is recieved the bot heads off to make entry/exit decisions
        :param subscribee: KlineDataMonitor
        :return: nothing
        """
        self.data = subscribee.data
        print(f"{self.name} looking for entry on {self.tf} for the {self.pair} trading pair:")
        print(self.data[-2:].to_string()+'\n\n')

        self.entry_exit()

    @abstractmethod
    def trade_history_build(self, exit_info):
        """
        :description: builds the final_trade obj to get pushed to the trade_history/{strategy}/{tf+pair} node
        :param exit_info:
        :return: json obj
        """
        pass

    @abstractmethod
    def strategy_indicators(self):
        pass
