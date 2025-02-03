########################################################### IMPORTS
# IMPORT SYS / OS
from sys import path as sys_path
from os import path as os_path
# IMPORT RANDOM
from random import random

########################################################### INITIALIZATION
# ADD current_script_path TO KNOWN PATHS
path = os_path.dirname(os_path.abspath(__file__))
if sys_path.count(path) == 0:
    sys_path.append(path)


########################################################### TRANSFER TYPES
class SettingData:
    """data type for transferring setting data"""
    def __init__(self, raw_data: str = "") -> None:
        self.separator = "~"

        self.win_size_percentage = [1, 0.25]
        self.win_bottom_offset = 0.335

        if raw_data:
            self.set(raw_data)

    def get(self) -> str:
        """returns settings as str"""
        output = ""

        output += str(self.win_size_percentage[0])
        output += self.separator
        output += str(self.win_size_percentage[1])
        output += self.separator

        output += str(self.win_bottom_offset)
        output += self.separator

        return output

    def set(self, raw_data: str) -> None:
        """sets variables based on raw_data input"""
        data = raw_data.split(self.separator)

        self.win_size_percentage = [float(data[0]), float(data[1])]
        self.win_bottom_offset = float(data[2])

class GameData:
    def __init__(self) -> None:
        self.counting: int = 0

        self.housing         : int = 10
        self.population      : int = 10
        self.food            : int = 100
        self.free_population : int = 0
        self.ascention       : int = 1
        self.battle_power    : int = 0

        self.resource : dict[str:int] = {
            "wood"    : 0,
            "stone"   : 0,
            "iron"    : 0,
            "fiber"   : 0,
            "kills"   : 0,
            "elements": 0,
            "steel"   : 0
        }

        self.production : dict[str:list[int, int]] = {
            "food" : [1, 0],
            "wood" : [1, 0],
            "stone": [1, 0],

            "fiber": [1, 0],
            "iron" : [1, 0],
            "steel": [1, 0],

            "elements": [1, 0]

        }

        self.click_wood     : int = 1
        self.click_stone    : int = 1
        self.click_fiber    : int = 1
        self.click_iron     : int = 1
        self.click_elements : int = 1
        self.click_food     : int = 1

        self.cost_fiber : int = 5
        self.cost_iron  : int = 5

        self.stats : dict[str:int] = {
            "wood_gathered"    : 0,
            "stone_gathered"   : 0,
            "fiber_gathered"   : 0,
            "iron_gathered"    : 0,
            "elements_gathered": 0,
            "food_gathered"    : 0,
            "steel_gathered"   : 0,
            "kills_gathered"   : 0,

            "wood_clicked"    : 0,
            "stone_clicked"   : 0,
            "fiber_clicked"   : 0,
            "iron_clicked"    : 0,
            "elements_clicked": 0,
            "food_clicked"    : 0,

            "food_build" : 0,
            "wood_build" : 0,
            "stone_build": 0,
            "fiber_build": 0,
            "iron_build" : 0,
            "steel_build": 0,
            "elements_build": 0
        }

        self.build_housing_gain = 10

        self.battle_current_chance = 0
        self.battle_targets = 10
        self.battle_timer = -1
        self.battle_last = -1

    def data_to_str(self) -> str:
        text = ""

        text += str(self.counting) + "\n"

        text += str(self.housing) + "\n"
        text += str(self.population) + "\n"
        text += str(self.food) + "\n"
        text += str(self.free_population) + "\n"
        text += str(self.ascention) + "\n"
        text += str(self.battle_power) + "\n"

        text += str(self.resource["wood"]) + "\n"
        text += str(self.resource["stone"]) + "\n"
        text += str(self.resource["iron"]) + "\n"#
        text += str(self.resource["fiber"]) + "\n"
        text += str(self.resource["kills"]) + "\n"
        text += str(self.resource["elements"]) + "\n"
        text += str(self.resource["steel"]) + "\n"

        text += str(self.production["food"][0]) + "\n"
        text += str(self.production["food"][1]) + "\n"
        text += str(self.production["wood"][0]) + "\n"
        text += str(self.production["wood"][1]) + "\n"
        text += str(self.production["stone"][0]) + "\n"
        text += str(self.production["stone"][1]) + "\n"#
        text += str(self.production["fiber"][0]) + "\n"
        text += str(self.production["fiber"][1]) + "\n"
        text += str(self.production["iron"][0]) + "\n"
        text += str(self.production["iron"][1]) + "\n"
        text += str(self.production["steel"][0]) + "\n"
        text += str(self.production["steel"][1]) + "\n"
        text += str(self.production["elements"][0]) + "\n"
        text += str(self.production["elements"][1]) + "\n"

        text += str(self.click_wood) + "\n"
        text += str(self.click_stone) + "\n"#
        text += str(self.click_fiber) + "\n"
        text += str(self.click_iron) + "\n"
        text += str(self.click_elements) + "\n"
        text += str(self.click_food) + "\n"

        text += str(self.cost_fiber) + "\n"
        text += str(self.cost_iron) + "\n"

        text += str(self.stats["wood_gathered"]) + "\n"
        text += str(self.stats["stone_gathered"]) + "\n"
        text += str(self.stats["fiber_gathered"]) + "\n"
        text += str(self.stats["iron_gathered"]) + "\n"#
        text += str(self.stats["elements_gathered"]) + "\n"
        text += str(self.stats["food_gathered"]) + "\n"
        text += str(self.stats["steel_gathered"]) + "\n"
        text += str(self.stats["kills_gathered"]) + "\n"

        text += str(self.stats["wood_clicked"]) + "\n"
        text += str(self.stats["stone_clicked"]) + "\n"
        text += str(self.stats["fiber_clicked"]) + "\n"
        text += str(self.stats["iron_clicked"]) + "\n"
        text += str(self.stats["elements_clicked"]) + "\n"
        text += str(self.stats["food_clicked"]) + "\n"#

        text += str(self.stats["food_build"]) + "\n"
        text += str(self.stats["wood_build"]) + "\n"
        text += str(self.stats["stone_build"]) + "\n"
        text += str(self.stats["fiber_build"]) + "\n"
        text += str(self.stats["iron_build"]) + "\n"
        text += str(self.stats["steel_build"]) + "\n"
        text += str(self.stats["elements_build"]) + "\n"

        text += str(self.build_housing_gain) + "\n"

        text += str(int(self.battle_current_chance)) + "\n"
        text += str(self.battle_targets) + "\n"#
        text += str(self.battle_timer) + "\n"
        text += str(self.battle_last) + "\n"

        return text

    def str_to_data(self, text: str):
        if text:
            data = text.split("\n")
            self.counting = int(data[0])

            self.housing = int(data[1])
            self.population = int(data[2])
            self.food = int(data[3])
            self.free_population = int(data[4])
            self.ascention = int(data[5])
            self.battle_power = int(data[6])

            self.resource: dict[str:int] = {
                "wood": int(data[7]),
                "stone": int(data[8]),
                "iron": int(data[9]),
                "fiber": int(data[10]),
                "kills": int(data[11]),
                "elements": int(data[12]),
                "steel": int(data[13])
            }

            self.production: dict[str:list[int, int]] = {
                "food": [int(data[14]), int(data[15])],
                "wood": [int(data[16]), int(data[17])],
                "stone": [int(data[18]), int(data[19])],

                "fiber": [int(data[20]), int(data[21])],
                "iron": [int(data[22]), int(data[23])],
                "steel": [int(data[24]), int(data[25])],

                "elements": [int(data[26]), int(data[27])]

            }

            self.click_wood: int = int(data[28])
            self.click_stone: int = int(data[29])
            self.click_fiber: int = int(data[30])
            self.click_iron: int = int(data[31])
            self.click_elements: int = int(data[32])
            self.click_food: int = int(data[33])

            self.cost_fiber: int = int(data[34])
            self.cost_iron: int = int(data[35])

            self.stats: dict[str:int] = {
                "wood_gathered": int(data[36]),
                "stone_gathered": int(data[37]),
                "fiber_gathered": int(data[38]),
                "iron_gathered": int(data[39]),
                "elements_gathered": int(data[40]),
                "food_gathered": int(data[41]),
                "steel_gathered": int(data[42]),
                "kills_gathered": int(data[43]),

                "wood_clicked": int(data[44]),
                "stone_clicked": int(data[45]),
                "fiber_clicked": int(data[46]),
                "iron_clicked": int(data[47]),
                "elements_clicked": int(data[48]),
                "food_clicked": int(data[49]),

                "food_build": int(data[50]),
                "wood_build": int(data[51]),
                "stone_build": int(data[52]),
                "fiber_build": int(data[53]),
                "iron_build": int(data[54]),
                "steel_build": int(data[55]),
                "elements_build": int(data[56])
            }

            self.build_housing_gain = int(data[57])

            self.battle_current_chance = int(data[58])
            self.battle_targets = int(data[59])
            self.battle_timer = int(data[60])
            self.battle_last = int(data[61])

    def ascention_get(self, specific: str) -> int:
        if specific == "po":
            return self.population // 50_000
        elif specific == "re":
            return sum(self.resource.values()) // 500_000
        elif specific == "bu":
            all = 0
            for product in self.production.values():
                all += product[1]
            return all // 25
        elif specific == "ba":
            return self.battle_power // 100
        else:
            return self.ascention_get("po") + self.ascention_get("re") + self.ascention_get("bu") + self.ascention_get("ba")

    def ascend_now(self):
        self.ascention = self.ascention_get("all")

        self.counting = 0

        self.housing = 10
        self.population = 10
        self.food = 100
        self.free_population = 0
        self.battle_power = 0

        self.resource = {
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "fiber": 0,
            "kills": 0,
            "elements": 0,
            "steel": 0
        }

        self.production = {
            "food": [1, 0],
            "wood": [1, 0],
            "stone": [1, 0],

            "fiber": [1, 0],
            "iron": [1, 0],
            "steel": [1, 0],

            "elements": [1, 0]

        }

        self.click_wood = 1
        self.click_stone = 1
        self.click_fiber = 1
        self.click_iron = 1
        self.click_elements = 1
        self.click_food = 1

        self.cost_fiber = 5
        self.cost_iron = 5

        self.stats = {
            "wood_gathered": 0,
            "stone_gathered": 0,
            "fiber_gathered": 0,
            "iron_gathered": 0,
            "elements_gathered": 0,
            "food_gathered": 0,
            "steel_gathered": 0,
            "kills_gathered": 0,

            "wood_clicked": 0,
            "stone_clicked": 0,
            "fiber_clicked": 0,
            "iron_clicked": 0,
            "elements_clicked": 0,
            "food_clicked": 0,

            "food_build": 0,
            "wood_build": 0,
            "stone_build": 0,
            "fiber_build": 0,
            "iron_build": 0,
            "steel_build": 0,
            "elements_build": 0
        }

        self.build_housing_gain = 10

        self.battle_current_chance = 0
        self.battle_targets = 10
        self.battle_timer = -1
        self.battle_last = -1

    def resource_get(self, name: str) -> int:
        return self.resource[name]

    def resource_set(self, name: str, value: int) -> None:
        self.resource[name] = int(value)

    def resource_add(self, name: str, value: int) -> None:
        self.resource[name] += int(value)
        self.stats[name + "_gathered"] += int(value)

    def resource_take(self, name: str, value: int) -> None:
        self.resource[name] -= value

    def stat_add(self, name: str, value: int) -> None:
        self.stats[name] += value

    def stat_get(self, name: str) -> int:
        return self.stats[name]

    def production_get(self, name: str) -> int:
        return self.production[name][0] * self.production[name][1]

    def production_build(self, name: str) -> None:
        self.production[name][1] += 1
        self.stats[name + "_build"] += 1

    def production_upgrade(self, name: str) -> None:
        self.production[name][0] *= 2

    def update(self):
        self.counting += 1
        if self.counting == 60:
            self.counting = 0

            if self.population < 0:
                self.population = 0

            # worker pop calc
            self.free_population = self.population
            for production in self.production:
                self.free_population -= self.production_get(production)
            effectivity = 1
            if self.free_population < 0:
                effectivity = self.population / (self.population - self.free_population)

            # automation calc
            for production in self.production:
                value = int(self.production_get(production) * effectivity * self.ascention)
                if production == "food":
                    self.food += value
                elif production == "steel":
                    if self.resource_get("iron") >= value and self.resource_get("fiber") >= value:
                        self.resource_add(production, value)
                        self.resource_take("iron", value)
                        self.resource_take("fiber", value)
                elif production == "fiber":
                    if self.resource_get("wood") >= value:
                        self.resource_add(production, value)
                        self.resource_take("wood", value)
                elif production == "iron":
                    if self.resource_get("stone") >= value:
                        self.resource_add(production, value)
                        self.resource_take("stone", value)
                else:
                    self.resource_add(production, value)

            # food calc
            if self.food >= self.population * 0.1:
                self.food = max(int(round(self.food - (self.population * 0.1))), 0)
                # pop growth calc
                if self.housing > self.population:
                    self.population = min(int(round(self.population * 1.1)), self.housing)
            else:
                self.food = 0
                self.population = max(int(round(self.population * 0.9)), 0)

            # timers
            if self.battle_timer != -1:
                self.battle_timer -= 1
                if self.battle_timer == 0:
                    self.battle_timer = -1
                    if random() < self.battle_current_chance:
                        self.resource_add("kills", self.battle_targets)
                        self.battle_targets *= 2
                        self.battle_last = 1
                    else:
                        self.population -= self.battle_targets * 10
                        self.battle_last = 0



class Emit:
    def __init__(self, name: str, data: list[any]) -> None:
        self.name: str       = name
        self.data: list[any] = data