import logging

import MyLogger
from BotInterface import BotInterface
import pandas as pd
import pandas_ta as ta
from datetime import timedelta
from Globals import Entry, Exit, TIME_FRAME_TO_SEC, trade_duration, pnl

PPVI_HIGH = "ppvi_high"
PPVI_LOW = "ppvi_low"
logger = logging.getLogger('root')


class CSP(BotInterface):
    def __init__(self, name, tf, pair):
        super().__init__(name, tf, pair)
        self.last_purchase_price = 0
        self.PPVI_PERIOD = 5
        self.force_entry = False
        self.force_exit = False
        self.in_trade = 0

    def entry_exit(self):
        stop_loss_percent = 1
        take_profit_percent = 2

        candle = self.strategy_indicators()
        # The addition of a candle stick interval to the timestamp is that the decision of an entry/exit is based on
        # the most recent close time, but the timestamp is an interval ago. EX: Enters based on 5m 11:25candle close
        # by which time it closes is actually 11:30. Thus, entry is 11:30 not 11:25
        timestamp = str(candle.index[0] + timedelta(seconds=TIME_FRAME_TO_SEC[self.tf]))
        price = float(candle['Close'][0])
        ppvi_high_band = float(candle['PPVI_HIGH'][0])
        ppvi_low_band = float(candle['PPVI_LOW'][0])

        long_entry_signals = 0
        short_entry_signals = 0
        # Long Checks
        if price < ppvi_low_band:
            long_entry_signals += 1

        # Short Checks
        if price > ppvi_high_band:
            short_entry_signals += 1

        # Take Profit
        is_take_profit = False
        if self.long_hold == 1:
            is_take_profit = price > ppvi_high_band or price > self.last_purchase_price * (
                    1 + (take_profit_percent / 100))
        if self.short_hold == 1:
            is_take_profit = price < ppvi_low_band or price < self.last_purchase_price * (1 - (
                    take_profit_percent / 100))

        # Stop Loss
        is_stop_loss = False
        if self.long_hold == 1:
            is_stop_loss = price < self.last_purchase_price * (1 - (stop_loss_percent / 100))

        if self.short_hold == 1:
            is_stop_loss = price > self.last_purchase_price * (1 + (stop_loss_percent / 100))

        entry_info = {
            "time_in": timestamp,
            "position": "",
            "price_entry": price,
            "ppvi_high": ppvi_high_band,
            "ppvi_low": ppvi_low_band
        }

        exit_info = {
            "time_out": timestamp,
            "price_exit": price,
            "ppvi_high": ppvi_high_band,
            "ppvi_low": ppvi_low_band
        }

        if self.force_exit and self.in_trade == 1:
            self.exit(exit_info)
            self.in_trade = 0
            return
        if self.force_entry:
            entry_info['position'] = "long"
            self.entry(entry_info)
            self.in_trade = 1
            return

        # Long Entry and Short Check Exit
        if self.long_hold == 0 and long_entry_signals >= 1:
            entry_info[Entry.POSITION.value] = "long"
            if self.short_hold == 1:
                self.exit(exit_info)
                self.short_hold = 0
            self.entry(entry_info)
            self.last_purchase_price = price
            self.long_hold = 1
        # Long Exit as stop loss or take profit
        elif self.long_hold == 1 and (is_take_profit or is_stop_loss):
            self.exit(exit_info)
            self.long_hold = 0
            self.last_purchase_price = 0

        # Short Entry and Long Exit Check
        if self.short_hold == 0 and short_entry_signals >= 1:
            entry_info[Entry.POSITION.value] = "short"
            if self.long_hold == 1:
                self.exit(exit_info)
                self.long_hold = 0
            self.entry(entry_info)
            self.last_purchase_price = price
            self.short_hold = 1
        # Short Exit as stop loss or take profit
        elif self.short_hold == 1 and (is_take_profit or is_stop_loss):
            self.exit(exit_info)
            self.short_hold = 0
            self.last_purchase_price = 0

        #Call trade_update (only has live_pnl for now) if no exit is made and in trade
        if self.long_hold == 1 or self.short_hold == 1:
            self.trade_update(price)

    def trade_history_build(self, exit_info):
        # First get entry info
        entry_info = self.ref_entry.get()

        # Merge the entry and exit info into one dict for the trade_history node in the db
        try:
            finished_trade = {
                Entry.TIME_IN.value: entry_info[Entry.TIME_IN.value],
                Exit.TIME_OUT.value: exit_info[Exit.TIME_OUT.value],
                Entry.POSITION.value: entry_info[Entry.POSITION.value],
                Entry.PRICE_ENTRY.value: entry_info[Entry.PRICE_ENTRY.value],
                Exit.PRICE_EXIT.value: exit_info[Exit.PRICE_EXIT.value],
                PPVI_LOW: exit_info[PPVI_HIGH],
                PPVI_HIGH: exit_info[PPVI_LOW],
                Exit.PNL.value: pnl(entry_info[Entry.POSITION.value], float(entry_info[Entry.PRICE_ENTRY.value]),
                                    float(exit_info[Exit.PRICE_EXIT.value])),
                Exit.TRADE_DURATION.value: trade_duration(entry_info[Entry.TIME_IN.value], exit_info[
                    Exit.TIME_OUT.value])
            }
        except ValueError:
            logging.warning(f'{self.name} on {self.tf} and trading pair {self.pair} is unable to create final trade'
                            f'metrics metrics returning empty final trade')
            finished_trade = {
                Entry.TIME_IN.value: "",
                Exit.TIME_OUT.value: "",
                Entry.POSITION.value: "",
                Entry.PRICE_ENTRY.value: "",
                Exit.PRICE_EXIT.value: "",
                PPVI_LOW: "",
                PPVI_HIGH: "",
                Exit.PNL.value: "",
                Exit.TRADE_DURATION.value: ""
            }

        return finished_trade

    def strategy_indicators(self):
        df = self.data
        df["PPVI_HIGH"] = self.PPVI_BAND(self.PPVI_PERIOD, "High")
        df["PPVI_LOW"] = self.PPVI_BAND(self.PPVI_PERIOD, "Low")

        return df[-2:-1]

    def PPVI_BAND(self, period, high_low) -> pd.DataFrame:
        df = self.data
        rolling_price_sma = df.ta.sma(length=period)

        # calculate rolling 3 period std off the highs
        rolling_std = df[high_low].rolling(period).std()
        # calculate rolling sma 3 off std highs series
        rolling_ppvi_vol = ta.sma(rolling_std, length=period) * 2

        # calculate bands
        if high_low == 'High':
            band = rolling_price_sma + rolling_ppvi_vol
        else:
            band = rolling_price_sma - rolling_ppvi_vol
        column_name = 'SMA_' + str(period)
        final = pd.DataFrame(index=df.index, data=band, columns=[column_name])

        return final
