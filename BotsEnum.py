from enum import Enum
from quants.mica.KrownCross import KrownCross
from quants.mica.CSP import CSP


class BotsEnum(Enum):
    KROWNCROSS = KrownCross
    CSP = CSP

bots_enum_dict = {
    "krowncross": BotsEnum.KROWNCROSS,
    "csp": BotsEnum.CSP
}
