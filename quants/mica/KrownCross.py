import datetime
from logging import ERROR, WARNING, INFO
import logging
from BotInterface import BotInterface
import pandas_ta as ta
import numpy as np
import pandas as pd
from datetime import timedelta
from Globals import TIME_FRAME_TO_SEC, trade_duration, pnl
from datetime import datetime
from Globals import Entry, Exit, Current, LTO

EMA_F = 9 #f = fast
EMA_M = 21 #m = medium
EMA_S = 55 # s = slow
EMA = 'EMA_'
separation = 2
bbwp_entry_signal = 60
bbwp_exit_signal = 70
bbwp_hit_counter = 0


BBWP_ENTRY = "bbwp_entry"
BBWP_EXIT = "bbwp_exit"
CLOSE = "Close"
BBWP = "BBWP"
EMA_F_STR = "ema_f"
EMA_M_STR = "ema_m"
EMA_S_STR = "ema_s"
EMA_M_SEP = "ema_m_sep"

#Stop Losses
SL_EMAF_LT_EMAM = "sl_emaf_lt_emam"
SL_P_LT_EMAS = "sl_p_lt_emas"

#Take Profit
TP_BBWP_HITS = "tp_bbwp_hits"

logger = logging.getLogger('root')


def current_ind_eval(ema_f, ema_m, ema_s, ema_m_s, bbwp):
    bbwp_b = "false"
    ema_sep_b = "false"

    # long bools
    ema_f_l_b = "false"
    ema_m_l_b = "false"
    ema_s_l_b = "false"

    # short bools
    ema_f_s_b = "false"
    ema_m_s_b = "false"
    ema_s_s_b = "false"

    if bbwp <= bbwp_entry_signal:
        bbwp_b = "true"

    if ema_m_s <= separation:
        ema_sep_b = "true"

    # case 1:
    if ema_f > ema_m > ema_s:
        # long
        ema_f_l_b = "true"
        ema_m_l_b = "true"
        ema_s_l_b = "true"
        # short
    # case 2:
    if ema_m > ema_f > ema_s:
        # long
        ema_m_l_b = "true"
        ema_s_l_b = "true"
        # short
    # case 3:
    if ema_m > ema_s > ema_f:
        # long
        ema_m_l_b = "true"
        # short
        ema_f_s_b = "true"
    # case 4:
    if ema_s > ema_m > ema_f:
        # long
        # short
        ema_f_s_b = "true"
        ema_m_s_b = "true"
        ema_s_s_b = "true"
    # case 5:
    if ema_f > ema_s > ema_m:
        # long
        ema_f_l_b = "true"
        # short
        ema_m_s_b = "true"

    # case 6
    if ema_s > ema_f > ema_m:
        # long
        # short
        ema_m_s_b = "true"
        ema_s_s_b = "true"

    current_ind_long = {
        EMA_F_STR: ema_f_l_b,
        EMA_M_STR: ema_m_l_b,
        EMA_S_STR: ema_s_l_b,
        EMA_M_SEP: ema_sep_b,
        BBWP: bbwp_b
    }
    current_ind_short = {
        EMA_F_STR: ema_f_s_b,
        EMA_M_STR: ema_m_s_b,
        EMA_S_STR: ema_s_s_b,
        EMA_M_SEP: ema_sep_b,
        BBWP: bbwp_b
    }

    return current_ind_long, current_ind_short


class KrownCross(BotInterface):
    def __init__(self, name, tf, pair):
        super().__init__(name, tf, pair)
        self.bbwp_hit_counter = 0
        self.trade_force_count = 0
        self.LIVE_TRADE_OBJECT = {self.entry_name:
            {
                LTO.LIVE_TRADE.value:
                    {Entry.IN_TRADE.value: "false",
                     Entry.LIVE_PNL.value: "",
                     Entry.TRADE_DURATION.value: "",
                     Entry.POSITION.value: "",
                     BBWP_ENTRY: "",
                     EMA_F_STR: "",
                     EMA_M_STR: "",
                     EMA_S_STR: "",
                     Entry.PRICE_ENTRY.value: "",
                     Entry.TIME_IN.value: ""
                     },
                LTO.CURRENT_IND_VAL.value:
                    {
                        EMA_F_STR: "",
                        EMA_M_STR: "",
                        EMA_S_STR: "",
                        EMA_M_SEP: "",
                        BBWP: "",
                        Entry.LAST_CLOSING_PRICE.value: "",
                        SL_EMAF_LT_EMAM: "",
                        SL_P_LT_EMAS: "",
                        TP_BBWP_HITS: ""
                    },
                LTO.CURRENT_IND_LONG.value:
                    {
                        EMA_F_STR: "false",
                        EMA_M_STR: "false",
                        EMA_S_STR: "false",
                        EMA_M_SEP: "false",
                        BBWP: "false"
                    },
                LTO.CURRENT_IND_SHORT.value:
                    {
                        EMA_F_STR: "false",
                        EMA_M_STR: "false",
                        EMA_S_STR: "false",
                        EMA_M_SEP: "false",
                        BBWP: "false"
                    }
            }
        }

    def entry_exit(self):
        # candle is a data frame of a single row containing the most recent candle close to which to apply trade
        # logic on
        candle = self.strategy_indicators()
        #The addition of a candle stick interval to the timestamp is that the decision of an entry/exit is based on
        # the most recent close time, but the timestamp is an interval ago. EX: Enters based on 5m 11:25candle close
        # by which time it closes is actually 11:30. Thus, entry is 11:30 not 11:25
        timestamp = str(candle.index[0]+timedelta(seconds=TIME_FRAME_TO_SEC[self.tf]))
        ema_f = float(candle[EMA+str(EMA_F)][0])
        ema_m = float(candle[EMA+str(EMA_M)][0])
        ema_s = float(candle[EMA+str(EMA_S)][0])
        price = float(candle[CLOSE][0])
        bbwp = candle[BBWP][0]

        # print(f"{self.name} is evaluating the below candle for the {self.pair} on the {self.tf} timeframe\n"
        #       f"{candle.to_string()}\n\n")
        bbwp_hit_exit = 3

        long_entry_signals = 0
        short_entry_signals = 0

        seperation_calc = abs((price - ema_m) / ema_m) * 100

        current_ind_long, current_ind_short = current_ind_eval(ema_f, ema_m, ema_s, seperation_calc, bbwp)

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

        current_ind = {
            EMA_F_STR: ema_f,
            EMA_M_STR: ema_m,
            EMA_S_STR: ema_s,
            EMA_M_SEP: seperation_calc,
            BBWP: bbwp,
            Entry.LAST_CLOSING_PRICE.value: price,
            SL_EMAF_LT_EMAM:  True if ema_f < ema_m else False,
            SL_P_LT_EMAS: True if price < ema_s else False,
            TP_BBWP_HITS: self.bbwp_hit_counter
        }

        live_entry_info = {
            Entry.IN_TRADE.value: "",
            Entry.TIME_IN.value: timestamp,
            Entry.TRADE_DURATION.value: "",
            Entry.POSITION.value: "",
            Entry.PRICE_ENTRY.value: price,
            BBWP_ENTRY: bbwp,
            EMA_F_STR: ema_f,
            EMA_M_STR: ema_m,
            EMA_S_STR: ema_s,
            Entry.LIVE_PNL.value: ""
        }

        exit_info = {
            Exit.TIME_OUT.value: timestamp,
            Exit.PRICE_EXIT.value: price,
            BBWP_EXIT: bbwp
        }

        # Long entry
        if self.long_hold == 0 and long_entry_signals == 3:
            live_entry_info[Entry.POSITION.value] = "long"
            live_entry_info[Entry.IN_TRADE.value] = "true"
            if self.short_hold == 1:
                self.exit(exit_info)
                self.short_hold = 0
            self.entry(live_entry_info)
            self.last_purchase_price = price
            self.long_hold = 1

        # Long exit
        elif self.long_hold == 1 and (is_take_profit or is_stop_loss):
            self.exit(exit_info)
            self.long_hold = 0
            self.last_purchase_price = 0
            self.bbwp_hit_counter = 0

        if self.short_hold == 0 and short_entry_signals == 3:
            live_entry_info[Entry.POSITION.value] = "short"
            live_entry_info[Entry.IN_TRADE.value] = "true"
            if self.long_hold == 1:
                self.exit(exit_info)
                self.long_hold = 0
            self.entry(live_entry_info)
            self.last_purchase_price = price
            self.short_hold = 1
        # Short exit
        elif self.short_hold == 1 and (is_take_profit or is_stop_loss):
            self.exit(exit_info)
            self.short_hold = 0
            self.last_purchase_price = 0
            self.bbwp_hit_counter = 0

        #Call trade_update (only has live_pnl for now) if no exit is made and in trade
        if self.long_hold == 1 or self.short_hold == 1:
            self.trade_update(price)

        #Regardless of trade all entry_names (Tf+pair) need to get current indicators updated
        self.ind_update(current_ind, current_ind_long, current_ind_short)


    def trade_history_build(self, exit_info):
        #First get entry info
        entry_info = self.ref_entry.get().to_dict()[self.entry_name][LTO.LIVE_TRADE.value]

        # Merge the entry and exit info into one dict for" the trade_history node in the db
        try:
            finished_trade = {
                Entry.TIME_IN.value: entry_info[Entry.TIME_IN.value],
                Exit.TIME_OUT.value: exit_info[Exit.TIME_OUT.value],
                Entry.POSITION.value: entry_info[Entry.POSITION.value],
                Entry.PRICE_ENTRY.value: entry_info[Entry.PRICE_ENTRY.value],
                Exit.PRICE_EXIT.value: exit_info[Exit.PRICE_EXIT.value],
                BBWP_ENTRY: entry_info[BBWP_ENTRY],
                BBWP_EXIT: exit_info[BBWP_EXIT],
                Exit.PNL.value: pnl(entry_info[Entry.POSITION.value], float(entry_info[Entry.PRICE_ENTRY.value]),
                               float(exit_info[Exit.PRICE_EXIT.value])),
                Current.TRADE_DURATION.value: trade_duration(entry_info[Entry.TIME_IN.value], exit_info[Exit.TIME_OUT.value])
            }
        except ValueError:
            logging.warning(f'{self.name} on {self.tf} and trading pair {self.pair} is unable to create final trade '
                            f'metrics metrics returning empty final trade')
            finished_trade = {
                Entry.TIME_IN.value: "",
                Exit.TIME_OUT.value: "",
                Entry.POSITION.value: "",
                Entry.PRICE_ENTRY.value: "",
                Exit.PRICE_EXIT.value: "",
                BBWP_ENTRY: "",
                BBWP_EXIT: "",
                Exit.PNL.value: "",
                Current.TRADE_DURATION.value: ""
            }

        return finished_trade

    def strategy_indicators(self):
        df = self.data

        # Columns names for ema will be as such: "EMA_{period}, ex: "EMA_9"
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=21, append=True)
        df.ta.ema(length=55, append=True)
        df[BBWP] = self.BBWP()

        return df[-2:-1]

    def BBWP(self):
        df = self.data
        STD = 2.0
        length = 13
        BBW = "BBB_"+str(length)+"_"+str(STD)
        LOOKBACK = 252
        bbands_series = ta.bbands(df[Entry.CLOSE.value].astype(float), std=STD, mamode='sma', length=13)
        BBW = bbands_series[BBW]
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
        bbwp_series = pd.DataFrame(index=bbands_series.index, data=bbwp_series, columns=[BBWP])

        return bbwp_series



