import logging
from abc import ABCMeta, abstractmethod
from pandas import DataFrame
from firebase_admin import db
from Globals import LIVE_PNL, pnl, Entry, Exit
logger = logging.getLogger('root')


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
        logging.info(f'{self.name} IS MAKING ENTRY ON {self.tf} for {self.pair} with the following:\n{entry_info}\n')
        self.ref_entry.set(entry_info)

    def exit(self, exit_info):
        """
        :description: handles the mock exit for a trade and stores the trade values to db in the trade history node
        :param exit_info: The exit_info json object contains the entirety of a trade for a given bot which contains
            all entry and exit info of the indicators for the strategy along with the candle metrics. TODO: add in
            trade metrics
        :return: Nothing, is a db management function
        """
        finished_trade = self.trade_history_build(exit_info)
        logging.info(f'{self.name} IS EXITING ON {self.tf} for {self.pair} with the following:\n{exit_info}\n')

        self.ref_trade_history.push(finished_trade)
        # Remove entry from db
        self.ref_entry.set("null")

    def trade_update(self, current_price):
        '''
        :description: Currently updates the current trades pnl after the most recent candle closure. If an exit isn't made
        :param entry_info:
        :return: None
        '''
        try:
            entry = self.ref_entry.get()
            entry[LIVE_PNL] = pnl(entry[Entry.POSITION.value], entry[Entry.PRICE_ENTRY.value], current_price)
            self.ref_entry.update(entry)
        except ConnectionError:
            logging.error(f'{self.name} with timeframe {self.tf} and pair {self.pair}'
                          f'through had BotInterface: THERE HAS BEEN AN ISSUE CONNECTING OR RECEIVING DATA FOR TRADE'
                          f'UPDATE\nLIVE PNL FOR THIS BOT WILL REMAIN AS IS')

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
        logging.info(f'{self.name} looking for entry on {self.tf} for the {self.pair} pair')
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
