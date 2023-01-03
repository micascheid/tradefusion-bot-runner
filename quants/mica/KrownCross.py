from BotInterface import BotInterface
import pandas_ta as ta
import numpy as np
import pandas as pd
from firebase_admin import db
from datetime import timedelta
from Globals import TIME_FRAME_TO_SEC, INTERVAL_UNITS

EMA_F = 9 #f = fast
EMA_M = 21 #m = medium
EMA_S = 55 # s = slow
separation = 2
bbwp_entry_signal = 60
bbwp_exit_signal = 70
bbwp_hit_counter = 0

TIME_IN = "time_in"
TIME_OUT = "time_out"
POSITION = "position"
PRICE_ENTRY = "price_entry"
PRICE_EXIT = "price_exit"
BBWP_ENTRY = "bbwp_entry"
BBWP_EXIT = "bbwp_exit"
CLOSE = "Close"
BBWP = "BBWP"


class KrownCross(BotInterface):

    def __init__(self, name, tf, pair):
        super().__init__(name, tf, pair)
        print("Being Created")
        self.bbwp_hit_counter = 0
        self.trade_force_count = 0

    def entry_exit(self):

        # candle is a data frame of a single row containing the most recent candle close to which to apply trade
        # logic on
        candle = self.strategy_indicators()
        #The addition of a candle stick interval to the timestamp is that the decision of an entry/exit is based on
        # the most recent close time, but the timestamp is an interval ago. EX: Enters based on 5m 11:25candle close
        # by which time it closes is actually 11:30. Thus, entry is 11:30 not 11:25
        timestamp = str(candle.index[0]+timedelta(seconds=TIME_FRAME_TO_SEC[self.tf]))
        ema_f = float(candle['EMA_9'][0])
        ema_m = float(candle['EMA_21'][0])
        ema_s = float(candle['EMA_55'][0])
        price = float(candle['Close'][0])
        bbwp = candle['BBWP'][0]
        bbwp_hit_exit = 3

        long_entry_signals = 0
        short_entry_signals = 0


        seperation_calc = abs((price - ema_m) / ema_m) * 100

        # Check 1: EMA Checks of 9>21>55
        if ema_f > ema_m > ema_s:
            long_entry_signals += 1

        if ema_f < ema_m < ema_s:
            short_entry_signals += 1

        # Check 2: Degree of separation check
        if seperation_calc <= separation:
            long_entry_signals += 1
            short_entry_signals += 1

        # Check 3: bbwp checks
        if bbwp < bbwp_entry_signal:
            long_entry_signals += 1
            short_entry_signals += 1

        # Take profit
        if bbwp >= bbwp_exit_signal:
            self.bbwp_hit_counter += 1

        is_take_profit = (self.long_hold == 1 and self.bbwp_hit_counter == bbwp_hit_exit) or (
                    self.short_hold == 1 and
                    self.bbwp_hit_counter == bbwp_hit_exit)

        # Stop loss
        is_stop_loss = False
        if self.long_hold == 1:
            is_stop_loss = self.long_hold == 1 and ema_f < ema_m or price <= ema_s
        if self.short_hold == 1:
            is_stop_loss = self.short_hold == 1 and ema_f > ema_m or price >= ema_s

        entry_info = {
            TIME_IN: timestamp,
            POSITION: "",
            PRICE_ENTRY: price,
            BBWP_ENTRY: bbwp
        }

        exit_info = {
            TIME_OUT: timestamp,
            PRICE_EXIT: price,
            BBWP_EXIT: bbwp
        }

        # Long entry
        if self.long_hold == 0 and long_entry_signals == 3:
            entry_info[POSITION] = "long"
            if self.short_hold == 1:
                self.exit(exit_info)
                self.short_hold = 0
            self.entry(entry_info)
            self.last_purchase_price = price
            self.long_hold = 1

        # Long exit
        elif self.long_hold == 1 and (is_take_profit or is_stop_loss):
            self.exit(exit_info)
            self.long_hold = 0
            self.last_purchase_price = 0
            self.bbwp_hit_counter = 0

        if self.short_hold == 0 and short_entry_signals == 3:
            entry_info[POSITION] = "short"
            if self.long_hold == 1:
                self.exit(exit_info)
                self.long_hold = 0
            self.entry(entry_info)
            self.last_purchase_price = price
            self.short_hold = 1
        # Short exit
        elif self.short_hold == 1 and (is_take_profit or is_stop_loss):
            self.exit(exit_info)
            self.short_hold = 0
            self.last_purchase_price = 0
            self.bbwp_hit_counter = 0

    def trade_history_build(self, exit_info):
        #First get entry info
        entry_info = self.ref_entry.get()

        # Merge the entry and exit info into one dict for the trade_history node in the db
        finished_trade = {
            "time_in": entry_info[TIME_IN],
            "time_out": exit_info[TIME_OUT],
            "long": entry_info[POSITION],
            "price_entry": entry_info[PRICE_ENTRY],
            "price_exit": exit_info[PRICE_EXIT],
            "bbwp_entry": entry_info[BBWP_ENTRY],
            "bbwp_exit": exit_info[BBWP_EXIT]
        }

        return finished_trade

    def strategy_indicators(self):
        df = self.data

        # Columns names for ema will be as such: "EMA_{period}, ex: "EMA_9"
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=21, append=True)
        df.ta.ema(length=55, append=True)
        df["BBWP"] = self.BBWP()

        return df[-2:-1]

    def BBWP(self):
        df = self.data
        STD = 2.0
        LOOKBACK = 252
        bbands_series = ta.bbands(df['Close'].astype(float), std=STD, mamode='sma', length=13)
        BBW = bbands_series['BBB_13_2.0']
        bbwp_series = np.array([])
        bbwp = [0.0] * LOOKBACK

        # make sure the series is at least as long as 252
        if len(BBW) > LOOKBACK:
            for current_bbw in range(LOOKBACK, len(BBW)):
                count = 0
                for bbw in range(current_bbw - LOOKBACK, current_bbw):
                    if BBW[bbw] < BBW[current_bbw]:
                        count += 1
                bbwp.append((count / LOOKBACK) * 100)
            bbwp_series = np.array(bbwp)
        bbwp_series = pd.DataFrame(index=bbands_series.index, data=bbwp_series, columns=['BBWP'])

        return bbwp_series

