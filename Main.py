########################################################### IMPORTS
# IMPORT SYS / OS
from sys import path as sys_path
from sys import exit as sys_exit
from sys import argv
from os import path as os_path, environ

# IMPORT PYGAME
import pygame
from pygame.locals import NOFRAME, SWSURFACE

# CUSTOM DATA TYPES
from scripts.DataTypes import SettingData, GameData

# CUSTOM COMPONENTS
from scripts.Tools import paths, file_settings_save, file_settings_load, file_settings_exists, file_game_save, file_game_load
from scripts.WindowComponents import SceneManager, Sound, mp3_path

# OTHER
from tkinter import Tk


########################################################### ARGV
DEV_MODE = False
if len(argv) > 0:
    for argument in argv:
        if argument == "reset":
            file_settings_save(SettingData())
            file_game_save(GameData().data_to_str())
        elif argument == "dev":
            DEV_MODE = True

########################################################### INITIALIZATION
# ADD current_script_path TO KNOWN PATHS
path = os_path.dirname(os_path.abspath(__file__))
if sys_path.count(path) == 0:
    sys_path.append(path)

# GET SCREEN SIZE
tool = Tk()
SCREEN_SIZE = (tool.winfo_screenwidth(), tool.winfo_screenheight())
del tool


########################################################### CONFIG
FPS_TARGET = 60

########################################################### CORE
pygame.init()

# LOAD SETTINGS
file_settings_exists()
settings = file_settings_load()

# SETTING WINDOW
WINDOW_SIZE = (SCREEN_SIZE[0] * settings.win_size_percentage[0], SCREEN_SIZE[1] * settings.win_size_percentage[1])
environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0, SCREEN_SIZE[1]-WINDOW_SIZE[1]-(SCREEN_SIZE[1]*settings.win_bottom_offset))
window = pygame.display.set_mode(WINDOW_SIZE, NOFRAME | SWSURFACE)

pygame.display.set_caption("OP_Final")
clock = pygame.time.Clock()

# GAME DATA
game_data = GameData()

# SETTING SCENE MANGER
scene_manger = SceneManager()
scene_manger.initialize(WINDOW_SIZE, game_data)
scene_manger.scenes["settings"].settings_link = settings
scene_manger.scenes["settings"].window_size = WINDOW_SIZE
scene_manger.scenes["settings"].screen_size = SCREEN_SIZE

# TOOL FUNCTIONS
def position_window(x, y):
    global window

    environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
    pygame.display.quit()
    pygame.display.init()
    window = pygame.display.set_mode(WINDOW_SIZE, NOFRAME | SWSURFACE)
scene_manger.scenes["settings"].redraw_window = position_window


########################################################### MAIN LOOP
game_data.str_to_data(file_game_load())
if DEV_MODE:
    scene_manger.switch_scene("game_build")
    game_data.population = 10000
    game_data.food = 1000000000
    game_data.resource = {
            "wood"    : 1000000000,
            "stone"   : 1000000000,
            "iron"    : 1000000000,
            "fiber"   : 1000000000,
            "kills"   : 1000000000,
            "elements": 1000000000,
            "steel"   : 1000000000
        }

music = Sound(mp3_path("music"), 0.05)
music.play(1000000)
running = True
save_interval = 100
while running:
    # EVENTS
    for event in pygame.event.get():
        # HANDLE MOUSE EVENTS
        if event.type == pygame.MOUSEBUTTONDOWN:
            scene_manger.handle_muse(event.button)

        # HANDLE KEYBOARD EVENTS
        elif event.type == pygame.KEYDOWN:
            # QUITTING
            if event.key == pygame.K_ESCAPE and event.mod & pygame.KMOD_SHIFT:
                if scene_manger.scene_current.name == "main_menu":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                else:
                    scene_manger.switch_scene("main_menu")
            elif event.key == pygame.K_ESCAPE:
                scene_manger.back_track()

            # OTHER
            key_name = pygame.key.name(event.key)
            key_name = key_name.replace('[', '').replace(']', '')
            scene_manger.handle_key(key_name)

        # HANDLE EVENTS
        elif event.type == pygame.QUIT:
            running = False
            file_game_save(game_data.data_to_str())
            break

    # UPDATE
    scene_manger.update(clock.get_time() / 1000)
    save_interval += clock.get_time() / 1000
    if save_interval >= 30:
        save_interval = 0
        file_game_save(game_data.data_to_str())

    # RENDER
    scene_manger.draw(window)
    pygame.display.flip()
    clock.tick(FPS_TARGET)


########################################################### EXIT
pygame.quit()
sys_exit()
