from BotsEnum import BotsEnum, bots_enum_dict
import BotInterface
from quants.mica.KrownCross import KrownCross
from quants.mica.CSP import CSP
from BotObj import BotObj


class BotFactory:
    def __init__(self, bot_obj_list):
        self.bot_obj_list = bot_obj_list

    def create(self):
        list_of_bots = []

        for bot_to_create in self.bot_obj_list:
            if bot_to_create.get_tf()+bot_to_create.get_pair() not in BotInterface.BotInterface.bots_created:
                list_of_bots.append(bots_enum_dict[bot_to_create.get_name()].value(tf=bot_to_create.get_tf(),
                                                                            pair=bot_to_create.get_pair()))

        return list_of_bots

