########################################################### IMPORTS
# IMPORT SYS / OS
import sys
from sys import path as sys_path
from os import path as os_path
from os import makedirs

# CUSTOM DATA TYPES
from DataTypes import SettingData

# OTHER
from enum import Enum


########################################################### INITIALIZATION
# ADD current_script_path TO KNOWN PATHS
path = os_path.dirname(os_path.abspath(__file__))
if sys_path.count(path) == 0:
    sys_path.append(path)


########################################################### FILE MANAGEMENT
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os_path.abspath(".")

    return os_path.join(base_path, relative_path)

def persistent_path(relative_path):
    home_directory = os_path.expanduser("~")
    persistent_directory = home_directory + r"\AppData\Local\ElementalVillage" + "\\" + relative_path
    return persistent_directory

class paths(Enum):
    SETTINGS = persistent_path(r"user\settings.txt")
    IMAGES = resource_path(r"resources\images")
    FONTS = resource_path(r"resources\fonts")
    GAME = persistent_path(r"user\save.txt")
    SOUND = resource_path(r"resources\sound")

def file_settings_save(data: SettingData) -> None:
    """saves settings into file"""
    with open(paths.SETTINGS.value, "w") as file:
        file.write(data.get())

def file_settings_load() -> SettingData:
    """loads settings into variable"""
    with open(paths.SETTINGS.value, "r") as file:
        data = SettingData(file.readline())

    return data

def file_settings_exists() -> None:
    if not os_path.exists(paths.SETTINGS.value):
        makedirs(persistent_path(r"\user"))
        file_settings_save(SettingData())

def file_game_save(text: str):
    with open(paths.GAME.value, "w") as file:
        file.write(text)

def file_game_load() -> str:
    """loads settings into variable"""
    try:
        with open(paths.GAME.value, "r") as file:
            data = file.readlines()
            output = "".join(data)
    except FileNotFoundError:
        output = ""

    return output