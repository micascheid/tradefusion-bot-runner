from enum import Enum
from BotsEnum import bots_enum_dict

class DBPaths(Enum):
    ACTIVEBOTS = 'active_bots'
    QUANTNAMES = 'quant_names'
    TIMEFRAMES_PAIRS = 'timeframe_pairs'


class DBLiveTrade(Enum):
    CSP = {"live_trade":
               {"in_trade": "",
                "live_pnl": "",
                "duration": "",
                "position": "",
                "ppvi_high": "",
                "ppvi_low": "",
                "price_entry": "",
                "time_in": ""},
           "current_ind":
               {"ppvi_high": "",
                "ppvi_low": ""
                }
           }
    KROWNCROSS = {"live_trade":
                      {"in_trade": "",
                       "live_pnl": "",
                       "duration": "",
                       "position": "",
                       "ppvi_high": "",
                       "ppvi_low": "",
                       "price_entry": "",
                       "time_in": ""},
                  "current_ind":
                      {"ppvi_high": "",
                       "ppvi_low": ""
                       }
                  }

DB_LIVE_TRADE_DICT = {}