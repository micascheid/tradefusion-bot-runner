from enum import Enum
from quants.mica.KrownCross import KrownCross
from quants.mica.CSP import CSP
from quants.edgeseeker.CSPV2 import CSPV2
from quants.edgeseeker.KrownCrossV2 import KrownCrossV2
class BotsEnum(Enum):
    KROWNCROSS = KrownCross
    KROWNCROSSV2 = KrownCrossV2
    CSP = CSP
    CSPV2 = CSPV2


bots_enum_dict = {
    "krowncross": BotsEnum.KROWNCROSS,
    "krowncrossv2": BotsEnum.KROWNCROSSV2,
    "csp": BotsEnum.CSP,
    "cspv2": BotsEnum.CSPV2
}
