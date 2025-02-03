########################################################### IMPORTS
# IMPORT SYS / OS
from sys import path as sys_path
from os import path as os_path

import pygame.event
# PYGAME
from pygame.surface import Surface
from pygame.image import load as image_load
from pygame import transform
from pygame.locals import SRCALPHA, HWSURFACE, SRCALPHA

# CUSTOM DATA TYPES
from DataTypes import Emit, GameData

# FILE TOOLS
from Tools import file_settings_save

# PATHS
from Tools import paths

# RANDOM
from random import randint

########################################################### INITIALIZATION
# ADD current_script_path TO KNOWN PATHS
path = os_path.dirname(os_path.abspath(__file__))
if sys_path.count(path) == 0:
    sys_path.append(path)


########################################################### VARIABLES
TEXT_FONT = "/excluded.ttf"
BUTTON_FONT = "/deep_shadow.ttf"
LOGO_FONT = "/fast_forward.ttf"

########################################################### TOOLS
def img_path(name: str) -> str:
    return paths.IMAGES.value+"/"+name

def mp3_path(name: str) -> str:
    return paths.SOUND.value+"/"+name+".mp3"

def int_smart_str(number: int) -> str:
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return str(number//1000) + " K"
    elif number < 1000000000:
        return str(number//1000000) + " M"
    elif number < 1000000000000:
        return str(number//1000000000) + " B"
    elif number < 1000000000000000:
        return str(number//1000000000000) + " T"

def component_shop_update_cost(comp: any, factor: float) -> None:
    x, y = comp.get_cost()
    comp.change_cost((x * factor, y * factor))

def generate_text_with_area_size(text: str, size: tuple[int, int], font_name: str, text_color: tuple[int, int, int] = (255, 255, 255)) -> Surface:
    font_size = 1
    while True:
        font = pygame.font.Font(paths.FONTS.value + font_name, font_size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()

        if text_width > size[0] or text_height > size[1]:
            font_size -= 1
            break
        font_size += 1

    return font.render(text, True, text_color)

def generate_text_with_font_size(text: str, font_size: int, font_name: str,  text_color: tuple[int, int, int] = (255, 255, 255)):
    font = pygame.font.Font(paths.FONTS.value + font_name, font_size)
    return font.render(text, True, text_color)

def generate_text_with_height(text: str, height: int, font_name: str, text_color: tuple[int, int, int] = (255, 255, 255)):
    font_size = 1
    while True:
        font = pygame.font.Font(paths.FONTS.value + font_name, font_size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()

        if text_height > height:
            font_size -= 1
            break
        font_size += 1

    return font.render(text, True, text_color)

########################################################### COMPONENTS
# BASE COMPONENT
class Sound:
    def __init__(self, path: str, volume: float = 0.7) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.sound = pygame.mixer.Sound(path)
        self.sound.set_volume(volume)

    def play(self, repeat=0):
        self.sound.play(repeat)

class Component:
    def __init__(self, tags: list[str], x: float, y: float, center: bool, update_func: callable, hover_func: callable) -> None:
        """Base component used to build other components can't be used on its own"""
        self.position_float : list[float]   = [x, y]
        self.tags           : list[str]     = tags
        self.emit           : list[Emit]    = []

        # EACH COMPONENT HAS TO CREATE ITS OWN SURFACE
        self.surface = None
        self.window_size    : list[int] = [-1, -1]
        self.position       : list[int] = [-1, -1]

        self.center = center
        self.update_function: callable = update_func
        self.hover_func     : callable = hover_func

        self.dt = 0.0
        self.initialized: bool = False

        # links
        self.component_manager_link = None
        self.scene_manager_link = None

    def move_x(self, x: float):
        self.position_float[0] += x
        self.position[0] = int(self.position_float[0] * self.window_size[0])
        if self.center:
            self.position[0] -= self.surface.width // 2

    def move_y(self, y: float):
        self.position_float[1] += y
        self.position[1] = int(self.position_float[1] * self.window_size[1])
        if self.center:
            self.position[1] -= self.surface.height // 2

    def move(self, x: float, y: float):
        self.move_x(x)
        self.move_y(y)

    def move_to(self, x: float, y: float):
        self.position_float = [x, y]
        self.move(0, 0)

    def get_position_float_centered(self) -> tuple[int, int]:
        x = int(self.position_float[0] * self.window_size[0]) - self.surface.width // 2
        y = int(self.position_float[1] * self.window_size[1]) - self.surface.height // 2
        return x, y

    def initialize(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_defaults(window_size, component_manager_link)

    def initialize_defaults(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager'):
        self.component_manager_link: ComponentManager = component_manager_link
        self.scene_manager_link: SceneManager = self.component_manager_link.scene_link.scene_manager_link
        self.initialized = True

    def draw(self) -> None:
        pass

    def update(self, dt) -> None:
        self.dt = dt
        if self.initialized:
            if self.update_function is not None:
                self.update_function(self)

            if self.hover_func is not None:
                # WTF TODO
                mouse_pos = pygame.mouse.get_pos()
                hovering = False
                if self.position[0] + self.surface.width > mouse_pos[0] > self.position[0]:
                    if self.position[1] + self.surface.height > mouse_pos[1] > self.position[1]:
                        hovering = True
                self.hover_func(self, hovering)

# BASIC COMPONENT
class Solid(Component):
    def __init__(self, x: float, y: float, w: float, h: float, color: tuple[int, int, int, int], center: bool = True, update_func: callable = None, hover_func: callable = None):
        super().__init__([], x, y, center, update_func, hover_func)
        self.w = w
        self.h = h

        self.color = color

    def initialize(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_defaults(window_size, component_manager_link)

        self.window_size = window_size
        # CREATE SURFACE
        self.surface: Surface = Surface((self.w * window_size[0], self.h * window_size[1]), SRCALPHA | HWSURFACE | SRCALPHA)

        # SET GLOBAL POSITION
        self.move(0, 0)
        self.draw()

    def draw(self) -> None:
        self.surface.fill(self.color)

    def change_color(self, new_color: tuple[int, int, int, int]):
        if self.color != new_color:
            self.color = new_color
            self.draw()

class Image(Component):
    def __init__(self, x: float, y: float, s: float, path: any, center: bool = True, update_func: callable = None, hover_func: callable = None, v_flip: bool = False, color: tuple[int, int, int, int] = None) -> None:
        """Component used for displaying image"""
        super().__init__([], x, y, center, update_func, hover_func)

        self.image_path : str       = None
        self.image      : Surface   = None
        if type(path) is str:
            self.image_path: str = path
            self.image: Surface = image_load(path)

            if self.image_path.split(".")[1] == "png":
                self.image.convert_alpha()
            else:
                self.image.convert()

        elif type(path) is Surface:
            self.image = path
            self.image.convert_alpha()
        else:
            raise AttributeError("Bad Type Input")

        self.color : tuple[int, int, int, int] = color

        self.s      : float = s
        self.v_flip : bool = v_flip

    def initialize(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_image(window_size, component_manager_link)
        self.draw()

    def initialize_image(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_defaults(window_size, component_manager_link)

        self.window_size = window_size
        # CREATE SURFACE
        aspect_ratio = self.image.width / self.image.height
        self.surface: Surface = Surface((self.s*window_size[1]*aspect_ratio, self.s*window_size[1]), SRCALPHA | HWSURFACE | SRCALPHA)

        # SET GLOBAL POSITION
        self.move(0, 0)

    def draw(self) -> None:
        self.surface.fill((0, 0, 0, 0))
        temp_image = transform.smoothscale(self.image, (self.surface.width, self.surface.height))
        if self.v_flip:
            temp_image = transform.flip(temp_image, False, True)
        self.surface.blit(temp_image, (0, 0))

        if self.color:
            self.modulate_color()

    def modulate_color(self, color: tuple[int, int, int, int] = None):
        if color:
            self.color = color
        if self.initialized and self.color is not None:
            temp_color = Surface(self.surface.size, pygame.SRCALPHA)
            temp_color.fill(self.color)
            self.surface.blit(temp_color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

class Text(Component):
    def __init__(self, x: float, y: float, s: float, text: str, color: tuple[int, int, int] = (255, 255, 255), center: bool = True, update_func: callable = None, hover_func: callable = None, dbg: bool = False, font_name: str = TEXT_FONT) -> None:
        """Component used for displaying image"""
        super().__init__([], x, y, center, update_func, hover_func)
        self.s              : float = s
        self.text_content   : str   = text

        self.font_name: str = font_name

        self.color: tuple[int, int, int] = color

        self.text_label = None

        self.dbg = dbg

    def initialize(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_text(window_size, component_manager_link)

        self.draw()

    def initialize_text(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_defaults(window_size, component_manager_link)

        self.window_size = window_size

        # CREATE SURFACE
        self.text_label: Surface = generate_text_with_height(self.text_content, int(self.window_size[1] * self.s), self.font_name, self.color)
        self.surface: Surface = Surface((self.text_label.width, self.text_label.height), SRCALPHA | HWSURFACE)

        # SET GLOBAL POSITION
        self.move(0, 0)

    def draw(self) -> None:
        self.surface.fill((0, 0, 0, 0))
        if self.dbg:
            self.surface.fill((255, 0, 255, 100))

        self.text_label = generate_text_with_height(self.text_content, int(self.window_size[1] * self.s), self.font_name, self.color)
        self.surface = Surface((self.text_label.width, self.text_label.height), SRCALPHA | HWSURFACE)
        x = (self.surface.width - self.text_label.width) // 2
        y = (self.surface.height - self.text_label.height) // 2
        self.surface.blit(self.text_label, (x, y))

        self.surface.blit(self.surface, (0, 0))

    def change_text(self, new_text: str):
        if str(new_text) != self.text_content:
            self.text_content = str(new_text)
            self.draw()
            self.move(0, 0)

    def change_color(self, new_color: tuple[int, int, int]):
        if new_color != self.color:
            self.color = new_color
            self.draw()

# COMPLEX COMPONENT
class ButtonText(Text):
    def __init__(self, x: float, y: float, s: float, text: str, click_func: callable = None, color: tuple[int, int, int] = (255, 255, 255), center: bool = True, update_func: callable = None, switch_scene: str = "", hover_func: callable = None, dbg: bool = False, font_name: str = TEXT_FONT):
        super().__init__(x, y, s, text, color, center, update_func, hover_func, dbg, font_name)
        self.tags = ["button"]
        self.function_click: callable = click_func
        self.switch_scene: str = switch_scene
        self.button_noize = Sound(mp3_path("button"), 0.1)

    def check_click(self, button) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if button == 1:
            if self.position[0] + self.surface.width > mouse_pos[0] > self.position[0]:
                if self.position[1] + self.surface.height > mouse_pos[1] > self.position[1]:
                    self.button_noize.play()
                    if self.function_click is not None:
                        self.function_click(self)
                    if self.switch_scene:
                        self.scene_manager_link.switch_scene(self.switch_scene)

class ButtonImage(Image):
    def __init__(self, x: float, y: float, s: float, path: any, click_func: callable = None, center: bool = True, update_func: callable = None, switch_scene: str = "", hover_func: callable = None, v_flip: bool = False, color: tuple[int, int, int, int] = None) -> None:
        """Component used for displaying image and also having clickable hit box"""
        super().__init__(x, y, s, path, center, update_func, hover_func, v_flip, color)
        self.tags = ["button"]
        self.function_click : callable  = click_func
        self.switch_scene   : str       = switch_scene
        self.button_noize = Sound(mp3_path("button"), 0.1)

    def check_click(self, button) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if button == 1:
            if self.position[0] + self.surface.width > mouse_pos[0] > self.position[0]:
                if self.position[1] + self.surface.height > mouse_pos[1] > self.position[1]:
                    self.button_noize.play()
                    if self.function_click is not None:
                        self.function_click(self)
                    if self.switch_scene:
                        self.scene_manager_link.switch_scene(self.switch_scene)

class ButtonImageText(ButtonImage):
    def __init__(self, x: float, y: float, s: float, path: str, text: str,  text_color: tuple[int, int, int], click_func: callable = None, text_scale: float = 1, center: bool = True, update_func: callable = None, switch_scene: str = "", hover_func: callable = None, v_flip: bool = False) -> None:
        super().__init__(x, y, s, path, click_func, center, update_func, switch_scene, hover_func, v_flip)
        self.raw_text: str = text
        self.text = None

        self.text_color: tuple[int, int, int]   = text_color
        self.text_scale: float                  = text_scale

    def initialize(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager') -> None:
        self.initialize_image(window_size, component_manager_link)

        scaled_size = (int(self.surface.width * self.text_scale), int(self.surface.height * self.text_scale))
        self.text: Surface = generate_text_with_area_size(self.raw_text, scaled_size, self.text_color)

        self.draw()

    def draw(self) -> None:
        super().draw()

        self.surface.blit(self.text, ((self.surface.width - self.text.width) // 2, (self.surface.height - self.text.height * 0.70) // 2))

# GAME SPECIFIC COMPONENTS
class ShopButton(Component):
    def __init__(self, x: float, y: float, s: float, img_bg: Surface, img_ico: str, cost: list[str, int], hover_text: str, emit: str, global_offset: tuple[int, int]=(0, 0)):
        def hover(self, state):
            if state:
                self.emit.append(Emit("HoverWindow", [self.hover_text]))
        super().__init__(["button"], x, y, False, None, hover)
        self.click_emit: str = emit

        self.img_bg : Surface = img_bg
        self.hover_text: str = hover_text

        self.global_offset: tuple[int, int] = global_offset

        self.img_ico: Surface = image_load(img_ico)
        self.img_ico.convert_alpha()

        self.init_cost0 = cost[2]
        self.init_cost1 = cost[5]

        self.cost: list[str, int] = cost
        self.cost_img0: Surface = image_load(img_path("Icons\\ico_" + cost[0] + ".png"))
        self.cost_img0.convert_alpha()
        self.cost_img1: Surface = image_load(img_path("Icons\\ico_" + cost[3] + ".png"))
        self.cost_img1.convert_alpha()

        self.s: float = s
        self.game_data: GameData = None

        self.button_noize = Sound(mp3_path("button"), 0.1)

    def initialize(self, window_size: tuple[int, int], component_manager_link: 'ComponentManager', game_data: GameData) -> None:
        self.initialize_defaults(window_size, component_manager_link)

        self.game_data = game_data
        self.window_size = window_size
        # CREATE SURFACE
        self.surface: Surface = Surface(((self.s * window_size[1])*5, self.s * window_size[1]), SRCALPHA | HWSURFACE | SRCALPHA)
        self.global_offset = (self.surface.width*self.global_offset[0]+1*self.global_offset[0], self.surface.height*self.global_offset[1]+1*self.global_offset[1])

        # SET GLOBAL POSITION
        self.move(0, 0)
        self.draw()

    def check_click(self, button) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if button == 1:
            if self.position[0] + self.surface.width > mouse_pos[0] > self.position[0]:
                if self.position[1] + self.surface.height > mouse_pos[1] > self.position[1]:
                    if self.game_data.resource_get(self.cost[1]) >= self.cost[2]:
                        if self.game_data.resource_get(self.cost[4]) >= self.cost[5]:
                            self.button_noize.play()
                            self.emit.append(Emit(self.click_emit, []))
                            self.game_data.resource_take(self.cost[1], self.cost[2])
                            self.game_data.resource_take(self.cost[4], self.cost[5])

    def reset(self):
        a, b, c, d, e, f = self.cost
        self.cost = [a, b, self.init_cost0, d, e, self.init_cost1]
        self.draw()

    def draw(self) -> None:
        self.surface.fill((0, 0, 0, 0))

        temp_bg = pygame.transform.smoothscale(self.img_bg, self.surface.size)
        self.surface.blit(temp_bg, (0, 0))

        temp_icon = pygame.transform.smoothscale(self.img_ico, (self.surface.height, self.surface.height))
        self.surface.blit(temp_icon, (0, 0))

        size = self.surface.height // 1.5
        temp_cost_0 = pygame.transform.smoothscale(self.cost_img0, (size, size))
        temp_cost_1 = pygame.transform.smoothscale(self.cost_img1, (size, size))
        self.surface.blit(temp_cost_0, (temp_icon.width+self.surface.width*0.1, 0))
        self.surface.blit(temp_cost_1, (temp_icon.width+(self.surface.width * 0.5), 0))

        temp_cost_text0 = generate_text_with_height(int_smart_str(self.cost[2]), int(self.surface.height//2.5), TEXT_FONT)
        self.surface.blit(temp_cost_text0, (temp_icon.width+self.surface.width*0.1, self.surface.height//2))
        temp_cost_text1 = generate_text_with_height(int_smart_str(self.cost[5]), int(self.surface.height//2.5), TEXT_FONT)
        self.surface.blit(temp_cost_text1, (temp_icon.width+(self.surface.width * 0.5), self.surface.height // 2))

    def get_cost(self) -> tuple[int, int]:
        return self.cost[2], self.cost[5]

    def change_cost(self, cost: tuple[int, int]) -> None:
        self.cost[2] = int(round(cost[0]))
        self.cost[5] = int(round(cost[1]))
        self.draw()

    def move_x(self, x: float):
        self.position_float[0] += x
        self.position[0] = int(self.position_float[0] * self.window_size[0]) + self.global_offset[0]

    def move_y(self, y: float):
        self.position_float[1] += y
        self.position[1] = int(self.position_float[1] * self.window_size[1]) + self.global_offset[1]


########################################################### SCENES
# NON GAME SCENES
class SceneBase:
    def __init__(self, name: str) -> None:
        self.name               : str              = name
        self.component_manager  : ComponentManager = ComponentManager()

        self.scene_manager_link = None

        self.create()

    def initialize(self, screen_size: tuple[int, int], scene_manager_link: 'SceneManager', game_data: GameData = None) -> None:
        self.scene_manager_link: SceneManager = scene_manager_link
        self.component_manager.initialize(screen_size, self, game_data)

    def new_comp(self, component: Component, comp_id: str = ""):
        self.component_manager.new_component(component, comp_id)

    def get_comp(self, comp_id: str):
        return self.component_manager.get_component(comp_id)

    def get_last_comp(self) -> Component:
        return list(self.component_manager.components.values())[-1]

    def draw(self, surface_target: Surface) -> None:
        self.component_manager.draw(surface_target)

    def update(self, dt: float) -> None:
        self.component_manager.update(dt)

    def handle_key(self, key: str) -> None:
        pass

    def handle_mouse(self, button: int) -> None:
        self.component_manager.handle_mouse(button)

    def handel_emit(self, emit: Emit):
        pass

    def on_scene_switch(self):
        pass

    def create(self) -> None:
        pass


class SceneMainMenu(SceneBase):
    def __init__(self) -> None:
        super().__init__("main_menu")
        self.initialized = False

    def create(self) -> None:


        # Hover Animation
        def anim_hover_change_color(self, state):
            try:
                self.hover_state_old
            except AttributeError:
                self.hover_state_old = state
                return

            if state != self.hover_state_old:
                if state:
                    self.color = (102, 79, 78)
                    self.draw()
                else:
                    self.color = (68, 53, 52)
                    self.draw()
                self.hover_state_old = state

        # BG
        self.new_comp(Image(0, 0, 1, img_path("Bg\\menu.png"), False))

        # BUTTONS
        def anim_slide_in_buttons(self):
            try:
                self.anim
            except AttributeError:
                self.anim = False
                self.anim_done = False

            if self.anim:
                target = 0.5
                if self.position_float[0] >= target:
                    self.position_float[0] = target
                    self.move_x(0)
                    self.update_function = None
                self.move_x((target - self.position_float[0] + 0.003) / 10)
        def on_click_start(self):
            try:
                self.clickable
            except AttributeError:
                self.clickable = True

            if self.anim_done and self.clickable:
                self.clickable = False
                self.scene_manager_link.history_add_self()
                self.emit.append(Emit("start_game", []))
        def on_click_settings(self):
            if self.anim_done:
                self.scene_manager_link.switch_scene("settings")
        def on_click_quit(self):
            pygame.event.post(pygame.event.Event(pygame.QUIT))


        self.new_comp(ButtonText(-1-0.15, 0.55, 0.2, "START", color=(68, 53, 52), font_name=BUTTON_FONT, click_func=on_click_start, update_func=anim_slide_in_buttons, hover_func=anim_hover_change_color), "button_start")
        self.new_comp(ButtonText(-1-0.15, 0.75, 0.16, "SETTINGS", color=(68, 53, 52), font_name=BUTTON_FONT, click_func=on_click_settings, update_func=anim_slide_in_buttons, hover_func=anim_hover_change_color), "button_settings")
        self.new_comp(ButtonText(-1-0.15, 0.92, 0.14, "QUIT", color=(68, 53, 52), font_name=BUTTON_FONT, click_func=on_click_quit, update_func=anim_slide_in_buttons, hover_func=anim_hover_change_color), "button_quit")

        # LOGO
        def anim_slide_in_logo(self):
            try:
                self.anim
            except AttributeError:
                self.anim = False

            if self.anim:
                target = 0.5
                if self.position_float[0] <= target:
                    self.position_float[0] = target
                    self.update_function = None
                    self.move_x(0)
                    self.emit.append(Emit("anim_done", []))
                self.move_x(-(self.position_float[0] + 0.003 - target) / 10)

        #self.new_comp(Solid(0.5, 0.125, 1, 0.23, (0, 0, 0, 100)))
        self.new_comp(Text(1+0.7, 0.195, 0.2813, "<ELEMENTAL>   <VILLAGE>", (102, 79, 78), update_func=anim_slide_in_logo, font_name=LOGO_FONT), "logo_b")
        self.new_comp(Text(1+0.7, 0.19, 0.28, "<ELEMENTAL>   <VILLAGE>", (68, 53, 52), update_func=anim_slide_in_logo, font_name=LOGO_FONT), "logo")

        # FLASH EFFECT
        def anim_flashbang_fadeout(self):
            if self.color != [255, 255, 255, 0]:
                r, g, b, a = self.color
                self.change_color([r, g, b, max(a-5, 0)])

        self.new_comp(Solid(0, 0, 1, 1, (255, 255, 255, 0), False, anim_flashbang_fadeout), "FlashBang")

        # Start Transition
        def anim_start_transition(self):
            try:
                self.anim_speed
            except AttributeError:
                self.anim_speed = 0

            if self.anim_speed != 0:
                if self.position_float[1] < -0.5:
                    self.move_y(0.001 * self.anim_speed)
                    self.anim_speed *= 1.1
                elif self.anim_speed != 0:
                    self.anim_speed = 0
                    self.emit.append(Emit("SwitchToGame", []))

        self.new_comp(Solid(0, 1.1, 1, 2, (34, 34, 34, 255), False, anim_start_transition), "StartAnim")

        # Init Transition
        def anim_init_transition(self):
            try:
                self.anim_speed
            except AttributeError:
                self.anim_speed = 1

            if self.position_float[1] < 1.1:
                self.move_y(0.001 * self.anim_speed)
                self.anim_speed *= 1.1
                r, g, b, a = self.color
                if r != 34:
                    self.change_color((r+0.5, g+0.5, b+0.5, a))
            elif self.anim_speed != 0:
                self.anim_speed = 0
                self.emit.append(Emit("ButtonSlide", []))

        self.new_comp(Solid(0, 0, 1, 1, (0, 0, 0, 255), False, anim_init_transition))


    def on_scene_switch(self):
        if self.initialized:
            self.get_comp("FlashBang").change_color((255, 255, 255, 100))
            self.get_comp("StartAnim").move_to(0, 1.1)
            self.get_comp("StartAnim").anim_speed = 0
            self.get_comp("button_start").clickable = True
        self.initialized = True

    def handel_emit(self, emit: Emit):
        if emit.name == "anim_done":
            self.get_comp("FlashBang").change_color((255, 255, 255, 255))
            self.get_comp("button_settings").anim_done = True
            self.get_comp("button_quit").anim_done = True
            self.get_comp("button_start").anim_done = True
        elif emit.name == "start_game":
            self.get_comp("StartAnim").anim_speed = 1
            self.get_comp("StartAnim").move_y(-3.1)
        elif emit.name == "SwitchToGame":
            self.scene_manager_link.switch_scene("game_build", False)
        elif emit.name == "ButtonSlide":
            self.get_comp("logo_b").anim = True
            self.get_comp("logo").anim = True
            self.get_comp("button_start").anim = True
            self.get_comp("button_settings").anim = True
            self.get_comp("button_quit").anim = True

class SceneSettings(SceneBase):
    def __init__(self) -> None:
        super().__init__("settings")
        self.settings_link = None
        self.redraw_window = None
        self.window_size = None
        self.screen_size = None

    def create(self) -> None:
        # Hover Animation
        def anim_hover_change_color(self, state):
            try:
                self.hover_state_old
            except AttributeError:
                self.hover_state_old = state
                return

            if state != self.hover_state_old:
                if state:
                    self.color = (102, 79, 78)
                    self.draw()
                else:
                    self.color = (68, 53, 52)
                    self.draw()
                self.hover_state_old = state

        # BG
        self.new_comp(Image(-0.2, 0, 1, img_path("Bg\\menu.png"), False))

        # APPLY / BACK
        def apply_settings(self):
            self.emit.append(Emit("change_settings", [float(self.component_manager_link.get_component("win_offset").text_content)]))

        self.new_comp(ButtonText(0.9, 0.8, 0.2, "APPLY", click_func=apply_settings, color=(68, 53, 52), font_name=BUTTON_FONT, hover_func=anim_hover_change_color))
        self.new_comp(ButtonText(0.1, 0.8, 0.2, "BACK", switch_scene="main_menu", color=(68, 53, 52), font_name=BUTTON_FONT, hover_func=anim_hover_change_color))

        # SETTING Window Offset
        x = 0.5
        y = 0.15

        def create_set_win_off(value):
            def set_win_off(self):
                label = self.component_manager_link.get_component("win_offset")
                label.change_text(str(round(float(label.text_content) + set_win_off.value, 3)))

            set_win_off.value = value
            return set_win_off

        self.new_comp(Solid(x, 0.5, 0.2, 0.9, (0, 0, 0, 50), True))
        self.new_comp(Text(x, y, 0.08, "Window Offset", color=(68, 53, 52)))
        self.new_comp(ButtonImage(x-0.015, y+0.2, 0.2, img_path("Buttons\\up_arrow.png"), click_func=create_set_win_off(0.001), color=(68, 53, 52, 255), hover_func=anim_hover_change_color))
        self.new_comp(ButtonImage(x+0.015, y+0.2, 0.2, img_path("Buttons\\up_arrow.png"), click_func=create_set_win_off(0.01), color=(68, 53, 52, 255), hover_func=anim_hover_change_color))
        self.new_comp(Text(x, y+0.4, 0.1, "0", color=(68, 53, 52)), "win_offset")
        self.new_comp(ButtonImage(x - 0.015, y+0.6, 0.2, img_path("Buttons\\up_arrow.png"), v_flip=True, click_func=create_set_win_off(-0.001), color=(68, 53, 52, 255), hover_func=anim_hover_change_color))
        self.new_comp(ButtonImage(x + 0.015, y+0.6, 0.2, img_path("Buttons\\up_arrow.png"), v_flip=True, click_func=create_set_win_off(-0.01), color=(68, 53, 52, 255), hover_func=anim_hover_change_color))

        # FLASH EFFECT
        def anim_flashbang_fadeout(self):
            if self.color != [255, 255, 255, 0]:
                r, g, b, a = self.color
                self.change_color([r, g, b, max(a-5, 0)])

        self.new_comp(Solid(0, 0, 1, 1, (255, 255, 255, 0), False, anim_flashbang_fadeout), "FlashBang")

    def on_scene_switch(self):
        self.component_manager.get_component("win_offset").change_text(str(self.settings_link.win_bottom_offset))
        self.get_comp("FlashBang").change_color((255, 255, 255, 100))

    def handel_emit(self, emit: Emit):
        if emit.name == "change_settings":
            self.settings_link.win_bottom_offset = emit.data[0]
            self.redraw_window(0, self.screen_size[1]-self.window_size[1]-(self.screen_size[1]*self.settings_link.win_bottom_offset))
            self.get_comp("FlashBang").change_color((0, 0, 0, 100))

            file_settings_save(self.settings_link)

# GAME SCENES
IMAGE_VERT_NAV_BUTTON = image_load(img_path("Ui\\button.png"))
IMAGE_VERT_NAV_BUILD = image_load(img_path("Buttons//btn_build.png"))
IMAGE_VERT_NAV_WORK = image_load(img_path("Buttons//btn_work.png"))
IMAGE_VERT_NAV_BATTLE = image_load(img_path("Buttons//btn_battle.png"))
IMAGE_VERT_NAV_ASCEND = image_load(img_path("Buttons//btn_ascend.png"))
IMAGE_VERT_NAV_STATS = image_load(img_path("Buttons//btn_stats.png"))
IMAGE_VERT_NAV_BACK = image_load(img_path("Buttons//btn_back.png"))
IMAGE_VERT_NAV_MENU = image_load(img_path("Buttons//btn_menu.png"))

IMAGE_TOP_BAR_BAR = image_load(img_path("Ui\\info_bar.png"))
IMAGE_TOP_BAR_BREAK = image_load(img_path("Ui\\info_bar_break.png"))
IMAGE_TOP_BAR_HOUSING = image_load(img_path("Icons\\ico_house.png"))
IMAGE_TOP_BAR_POPULATION = image_load(img_path("Icons\\ico_person.png"))
IMAGE_TOP_BAR_FOOD = image_load(img_path("Icons\\ico_food.png"))
IMAGE_TOP_BAR_FREE_POPULATION = image_load(img_path("Icons\\ico_shrug.png"))
IMAGE_TOP_BAR_ASCENTION = image_load(img_path("Icons\\ico_star.png"))
IMAGE_TOP_BAR_BATTLE_POWER = image_load(img_path("Icons\\ico_sword.png"))

IMAGE_EXTRA_PANEL = image_load(img_path("Ui\\panel.png"))
IMAGE_SHOP_BUTTON = image_load(img_path("Ui\\shop.png"))

IMAGE_ICON_WOOD = image_load(img_path("Icons\\ico_wood.png"))
IMAGE_ICON_STONE = image_load(img_path("Icons\\ico_stone.png"))
IMAGE_ICON_FIBER = image_load(img_path("Icons\\ico_fiber.png"))
IMAGE_ICON_IRON = image_load(img_path("Icons\\ico_iron.png"))
IMAGE_ICON_KILLS =image_load(img_path("Icons\\ico_skull.png"))
IMAGE_ICON_ELEMENTS = image_load(img_path("Icons\\ico_elements.png"))
IMAGE_ICON_STEEL = image_load(img_path("Icons\\ico_steel.png"))
class SceneGameBase(SceneBase):
    def __init__(self, name: str):
        super().__init__(name)

        self.game_data = None

        self.scene_transition: str = None
        self.scene_transition_n_skip: bool = None

    def initialize(self, screen_size: tuple[int, int], scene_manager_link: 'SceneManager', game_data: GameData = None) -> None:
        super().initialize(screen_size, scene_manager_link, game_data)
        self.game_data : GameData = game_data

    def custom_switch_scene(self, scene_name: str):
        if self.scene_transition is None and scene_name != self.scene_manager_link.scene_current.name:
            self.scene_transition = scene_name
            self.scene_transition_n_skip = True
            self.get_comp("AnimTransition").move_to(0, -1.6)
            self.get_comp("AnimTransition").anim_speed = 1

    def create(self) -> None:
        # VERTICAL SCENE MENU
        def anim_hover_vertical_menu(self, state):
            try:
                self.hover_state_old
            except AttributeError:
                self.hover_state_old = state
                return

            if state != self.hover_state_old:
                if state:
                    self.color = (102, 79, 78, 255)
                    self.draw()
                else:
                    self.color = (64, 41, 40, 255)
                    self.draw()
                self.hover_state_old = state
        def click(self):
            self.emit.append(Emit("BeginTransition", ["game_build", True]))
        size = 0.15
        self.new_comp(ButtonImage(0, 0, size, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0, size, IMAGE_VERT_NAV_BUILD, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))
        def click(self):
            self.emit.append(Emit("BeginTransition", ["game_work", True]))
        self.new_comp(ButtonImage(0, 0.15, size, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0.15, size, IMAGE_VERT_NAV_WORK, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))
        def click(self):
            self.emit.append(Emit("BeginTransition", ["game_battle", True]))
        self.new_comp(ButtonImage(0, 0.3, size, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0.3, size, IMAGE_VERT_NAV_BATTLE, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))
        def click(self):
            self.emit.append(Emit("BeginTransition", ["game_ascend", True]))
        self.new_comp(ButtonImage(0, 0.45, size, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0.45, size, IMAGE_VERT_NAV_ASCEND, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))
        def click(self):
            self.emit.append(Emit("BeginTransition", ["game_stats", True]))
        self.new_comp(ButtonImage(0, 0.6, size, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0.6, size, IMAGE_VERT_NAV_STATS, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))
        def click(self):
            self.scene_manager_link.back_track()
        self.new_comp(ButtonImage(0, 0.8, size-0.05, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0.8, size-0.05, IMAGE_VERT_NAV_BACK, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))
        def click(self):
            self.scene_manager_link.switch_scene("main_menu")
        self.new_comp(ButtonImage(0, 0.9, size-0.05, IMAGE_VERT_NAV_BUTTON, click, False))
        self.new_comp(Image(0, 0.9, size-0.05, IMAGE_VERT_NAV_MENU, False, color=(64, 41, 40, 255), hover_func=anim_hover_vertical_menu))

        # TOP INFO BAR
        x, spacing = 0.58, 0.032
        self.new_comp(Image(x, 0, 0.1, IMAGE_TOP_BAR_BAR, False))
        x += +0.01
        self.new_comp(Image(x, 0.045, 0.07, IMAGE_TOP_BAR_HOUSING, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing, 0.045, 0.07, "1 000 000", (64, 41, 40)), "top_bar_housing")
        self.new_comp(Image(x+spacing*2, 0.045, 0.07, IMAGE_TOP_BAR_POPULATION, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing*3, 0.045, 0.07, "1 000 000", (64, 41, 40)), "top_bar_population")
        self.new_comp(Image(x+spacing*4, 0.045, 0.07, IMAGE_TOP_BAR_FOOD, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing*5, 0.045, 0.07, "1 000 000", (64, 41, 40)), "top_bar_food")
        self.new_comp(Image(x+spacing*6, 0.045, 0.07, IMAGE_TOP_BAR_FREE_POPULATION, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing*7, 0.045, 0.07, "1 000 000", (64, 41, 40)), "top_bar_free_population")
        self.new_comp(Image(x+spacing*8, 0.045, 0.07, IMAGE_TOP_BAR_ASCENTION, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing*9, 0.045, 0.07, "1 000 000", (64, 41, 40)), "top_bar_ascention")
        self.new_comp(Image(x+spacing*10, 0.045, 0.1, IMAGE_TOP_BAR_BREAK))
        x += 0.01
        self.new_comp(Image(x+spacing*10, 0.045, 0.07, IMAGE_TOP_BAR_BATTLE_POWER, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing*11, 0.045, 0.07, "1 000 000/S", (64, 41, 40)), "top_bar_battle_power")

        # FLOATING TIP
        # TODO Floating Tip

        # TRANSITION
        def anim_transition(self):
            try:
                self.anim_speed
            except AttributeError:
                self.anim_speed = 0

            if self.position_float[1] < -0.25:
                self.move_y(0.001 * self.anim_speed)
                self.anim_speed *= 1.1
            elif self.anim_speed != 0:
                self.move_to(0, 0)
                self.anim_speed = 0
                self.emit.append(Emit("Transition", []))

        self.new_comp(Solid(0, -1.502, 1, 1.5, (34, 34, 34, 255), False, anim_transition), "AnimTransition")

        # INITIAL TRANSITION
        def anim_init_transition(self):
            try:
                self.anim_speed
            except AttributeError:
                self.anim_speed = 1

            if self.position_float[1] < 1.1:
                self.move_y(0.001 * self.anim_speed)
                self.anim_speed *= 1.1
            elif self.anim_speed != 0:
                self.anim_speed = 0

        self.new_comp(Solid(0, 0, 1, 1, (34, 34, 34, 255), False, anim_init_transition), "AnimInitTransition")

    def on_scene_switch(self):
        self.scene_transition = None

        self.get_comp("AnimInitTransition").move_to(0, 0)
        self.get_comp("AnimInitTransition").anim_speed = 1

        self.get_comp("AnimTransition").move_to(0, -1.502)
        self.get_comp("AnimTransition").anim_speed = 0

    def handel_emit(self, emit: Emit):
        if emit.name == "HoverWindow":
            pass
        if emit.name == "BeginTransition":
            self.custom_switch_scene(emit.data[0])
            self.scene_transition_n_skip = emit.data[1]
        elif emit.name == "Transition":
            self.scene_manager_link.switch_scene(self.scene_transition, self.scene_transition_n_skip)
            self.scene_transition = None
            self.scene_transition_n_skip = None

    def update(self, dt: float) -> None:
        super().update(dt)
        self.game_data.update()

        # TOP BAR
        self.get_comp("top_bar_housing").change_text(int_smart_str(self.game_data.housing))
        self.get_comp("top_bar_population").change_text(int_smart_str(self.game_data.population))
        self.get_comp("top_bar_food").change_text(int_smart_str(self.game_data.food))
        if self.game_data.food == 0 and self.get_comp("top_bar_food").color != (200, 0, 0, 255):
            self.get_comp("top_bar_food").color = (200, 0, 0, 255)
            self.get_comp("top_bar_food").draw()
        elif self.game_data.food > 0 and self.get_comp("top_bar_food").color != (64, 41, 40, 255):
            self.get_comp("top_bar_food").color = (64, 41, 40, 255)
            self.get_comp("top_bar_food").draw()
        self.get_comp("top_bar_free_population").change_text(int_smart_str(self.game_data.free_population))
        if self.game_data.free_population < 0 and self.get_comp("top_bar_free_population").color != (200, 0, 0, 255):
            self.get_comp("top_bar_free_population").color = (200, 0, 0, 255)
            self.get_comp("top_bar_free_population").draw()
        elif self.game_data.free_population > 0 and self.get_comp("top_bar_free_population").color != (64, 41, 40, 255):
            self.get_comp("top_bar_free_population").color = (64, 41, 40, 255)
            self.get_comp("top_bar_free_population").draw()
        self.get_comp("top_bar_ascention").change_text(int_smart_str(self.game_data.ascention))
        self.get_comp("top_bar_battle_power").change_text(int_smart_str(self.game_data.battle_power))


class SceneGameBuild(SceneGameBase):
    def __init__(self) -> None:
        super().__init__("game_build")

    def create(self) -> None:
        # BG
        self.new_comp(Image(0, 0, 1, img_path("Bg//grass.png"), False))

        # CLICKERS
        x = 0.52
        def tree_click(self):
            self.emit.append(Emit("gather_wood", []))
        self.new_comp(ButtonImage(x, 0.25, 0.4, img_path("Game\\tree_cluster.png"), tree_click))
        self.new_comp(Text(x, 0.25, 0.12, "1000000"), "click_wood")
        def stone_click(self):
            self.emit.append(Emit("gather_stone", []))
        self.new_comp(ButtonImage(x, 0.75, 0.4, img_path("Game\\stone_cluster.png"), stone_click))
        self.new_comp(Text(x, 0.75, 0.12, "1000000"), "click_stone")
        def food_click(self):
            self.emit.append(Emit("gather_food", []))
        self.new_comp(ButtonImage(x-0.05, 0.5, 0.4, img_path("Game\\wheat_patch.png"), food_click))
        self.new_comp(Text(x-0.05, 0.5, 0.12, "1000000"), "click_food")

        # EXTRA PANEL
        # EXTRA PANEL RESOURCES
        self.new_comp(Image(0.58, 0.2, 0.9, IMAGE_EXTRA_PANEL, False))
        x, y, spacing = 0.6, 0.28, 0.032
        self.new_comp(Image(x , y, 0.1, IMAGE_ICON_WOOD, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing, y, 0.07, "1 000 000", (64, 41, 40)), "resource_wood")
        self.new_comp(Image(x+spacing*2, y, 0.1, IMAGE_ICON_STONE, color=(0, 0, 0, 255)))
        self.new_comp(Text(x+spacing*3, y, 0.07, "1 000 000", (64, 41, 40)), "resource_stone")
        self.new_comp(Image(x + spacing * 4, y, 0.1, IMAGE_ICON_FIBER, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 5, y, 0.07, "1 000 000", (64, 41, 40)), "resource_fiber")
        self.new_comp(Image(x + spacing * 6, y, 0.1, IMAGE_ICON_IRON, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 7, y, 0.07, "1 000 000", (64, 41, 40)), "resource_iron")
        self.new_comp(Image(x + spacing * 8, y, 0.1, IMAGE_ICON_STEEL, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 9, y, 0.07, "1 000 000", (64, 41, 40)), "resource_steel")
        self.new_comp(Image(x + spacing * 10, y, 0.1, IMAGE_ICON_KILLS, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 11, y, 0.07, "1 000 000", (64, 41, 40)), "resource_kills")
        # EXTRA PANEL BUTTONS
        size = 0.15
        x, y = 0.59, 0.36
        # housing
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\housing.png"), ["wood", "wood", 10, "stone", "stone", 10], "hello", "shop_housing"), "shop_housing")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\housing_upgrade.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_housing_upgrade", (1, 0)), "shop_housing_upgrade")
        # food
        self.new_comp(ShopButton(x, y , size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\food.png"),["wood", "wood", 10, "fiber", "fiber", 10], "hello", "shop_food", (0, 1)), "shop_food")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\food_upgrade.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_food_upgrade", (1, 1)),"shop_food_upgrade")
        # wood
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\wood.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_wood", (0, 2)), "shop_wood")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\wood_upgrade.png"),["fiber", "fiber", 10, "steel", "steel", 10], "hello", "shop_wood_upgrade", (1, 2)),"shop_wood_upgrade")
        # wood
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\stone.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_stone", (0, 3)), "shop_stone")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\stone_upgrade.png"),["iron", "iron", 10, "steel", "steel", 10], "hello", "shop_stone_upgrade", (1, 3)),"shop_stone_upgrade")
        # mouse
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\mouse.png"),["steel", "steel", 10, "skull", "kills", 10], "hello", "shop_mouse", (2, 3)),"shop_mouse")

        # SUPER
        super().create()

    def handel_emit(self, emit: Emit):
        super().handel_emit(emit)

        if emit.name == "gather_wood":
            self.game_data.resource_add("wood", self.game_data.click_wood)
            self.game_data.stat_add("wood_clicked", self.game_data.click_wood)
        elif emit.name == "gather_stone":
            self.game_data.resource_add("stone", self.game_data.click_stone)
            self.game_data.stat_add("stone_clicked", self.game_data.click_wood)
        elif emit.name == "gather_food":
            self.game_data.food += self.game_data.click_food
            self.game_data.stat_add("food_clicked", self.game_data.click_wood)
            self.game_data.stat_add("food_gathered", self.game_data.click_wood)

        elif emit.name == "shop_housing":
            comp = self.get_comp("shop_housing")
            component_shop_update_cost(comp, 1.5)
            self.game_data.housing += self.game_data.build_housing_gain
        elif emit.name == "shop_housing_upgrade":
            comp = self.get_comp("shop_housing_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.build_housing_gain *= 2
            self.game_data.housing *= 2
        elif emit.name == "shop_food":
            comp = self.get_comp("shop_food")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("food")
        elif emit.name == "shop_food_upgrade":
            comp = self.get_comp("shop_food_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.production_upgrade("food")
        elif emit.name == "shop_wood":
            comp = self.get_comp("shop_wood")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("wood")
        elif emit.name == "shop_wood_upgrade":
            comp = self.get_comp("shop_wood_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.production_upgrade("wood")
        elif emit.name == "shop_stone":
            comp = self.get_comp("shop_stone")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("stone")
        elif emit.name == "shop_stone_upgrade":
            comp = self.get_comp("shop_stone_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.production_upgrade("stone")
        elif emit.name == "shop_mouse":
            comp = self.get_comp("shop_mouse")
            component_shop_update_cost(comp, 2)
            self.game_data.click_food *= 2
            self.game_data.click_wood *= 2
            self.game_data.click_stone *= 2

    def update(self, dt: float) -> None:
        super().update(dt)

        self.get_comp("resource_wood").change_text(int_smart_str(self.game_data.resource_get("wood")))
        self.get_comp("resource_stone").change_text(int_smart_str(self.game_data.resource_get("stone")))
        self.get_comp("resource_iron").change_text(int_smart_str(self.game_data.resource_get("iron")))
        self.get_comp("resource_fiber").change_text(int_smart_str(self.game_data.resource_get("fiber")))
        self.get_comp("resource_steel").change_text(int_smart_str(self.game_data.resource_get("steel")))
        self.get_comp("resource_kills").change_text(int_smart_str(self.game_data.resource_get("kills")))

        self.get_comp("click_wood").change_text("+" + int_smart_str(self.game_data.click_wood))
        self.get_comp("click_stone").change_text("+" + int_smart_str(self.game_data.click_stone))
        self.get_comp("click_food").change_text("+" + int_smart_str(self.game_data.click_food))

class SceneGameWork(SceneGameBase):
    def __init__(self) -> None:
        super().__init__("game_work")

    def create(self) -> None:
        # BG
        self.new_comp(Image(0, 0, 1, img_path("Bg//stone.png"), False))

        # CLICKERS
        x = 0.52
        def tree_click(self):
            self.emit.append(Emit("work_wood", []))
        self.new_comp(ButtonImage(x, 0.25, 0.4, img_path("Game\\axe.png"), tree_click))
        self.new_comp(Text(x, 0.25, 0.1, "1000000"), "click_fiber")
        def stone_click(self):
            self.emit.append(Emit("work_stone", []))
        self.new_comp(ButtonImage(x, 0.75, 0.4, img_path("Game\\pickaxe.png"), stone_click))
        self.new_comp(Text(x, 0.75, 0.1, "1000000"), "click_iron")

        # EXTRA PANEL
        self.new_comp(Image(0.58, 0.2, 0.9, IMAGE_EXTRA_PANEL, False))
        x, y, spacing = 0.6, 0.28, 0.032
        self.new_comp(Image(x, y, 0.1, IMAGE_ICON_WOOD, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing, y, 0.07, "1 000 000", (64, 41, 40)), "resource_wood")
        self.new_comp(Image(x + spacing * 2, y, 0.1, IMAGE_ICON_STONE, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 3, y, 0.07, "1 000 000", (64, 41, 40)), "resource_stone")
        self.new_comp(Image(x + spacing * 4, y, 0.1, IMAGE_ICON_FIBER, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 5, y, 0.07, "1 000 000", (64, 41, 40)), "resource_fiber")
        self.new_comp(Image(x + spacing * 6, y, 0.1, IMAGE_ICON_IRON, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 7, y, 0.07, "1 000 000", (64, 41, 40)), "resource_iron")
        self.new_comp(Image(x + spacing * 8, y, 0.1, IMAGE_ICON_STEEL, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 9, y, 0.07, "1 000 000", (64, 41, 40)), "resource_steel")
        self.new_comp(Image(x + spacing * 10, y, 0.1, IMAGE_ICON_KILLS, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 11, y, 0.07, "1 000 000", (64, 41, 40)), "resource_kills")
        # EXTRA PANEL BUTTONS
        size = 0.15
        x, y = 0.59, 0.36
        # fiber
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\fiber.png"),["wood", "wood", 10, "stone", "stone", 10], "hello", "shop_fiber"), "shop_fiber")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\fiber_upgrade.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_fiber_upgrade", (1, 0)),"shop_fiber_upgrade")
        # iron
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\iron.png"),["wood", "wood", 10, "fiber", "fiber", 10], "hello", "shop_iron", (0, 1)), "shop_iron")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\iron_upgrade.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_iron_upgrade", (1, 1)),"shop_iron_upgrade")
        # steel
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\steel.png"),["fiber", "fiber", 10, "iron", "iron", 10], "hello", "shop_steel", (0, 2)), "shop_steel")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\steel_upgrade.png"),["fiber", "fiber", 10, "steel", "steel", 10], "hello", "shop_steel_upgrade", (1, 2)),"shop_steel_upgrade")
        # mouse
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\mouse.png"),["steel", "steel", 10, "skull", "kills", 10], "hello", "shop_mouse", (0, 3)),"shop_mouse")

        # SUPER
        super().create()

    def handel_emit(self, emit: Emit):
        super().handel_emit(emit)

        if emit.name == "work_wood":
            if self.game_data.resource_get("wood") >= self.game_data.cost_fiber:
                self.game_data.resource_take("wood", self.game_data.cost_fiber)
                self.game_data.resource_add("fiber", self.game_data.click_fiber)
                self.game_data.stat_add("fiber_clicked", self.game_data.click_wood)
        elif emit.name == "work_stone":
            if self.game_data.resource_get("stone") >= self.game_data.cost_iron:
                self.game_data.resource_take("stone", self.game_data.cost_iron)
                self.game_data.resource_add("iron", self.game_data.click_iron)
                self.game_data.stat_add("iron_clicked", self.game_data.click_wood)

        elif emit.name == "shop_fiber":
            comp = self.get_comp("shop_fiber")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("fiber")
        elif emit.name == "shop_fiber_upgrade":
            comp = self.get_comp("shop_fiber_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.production_upgrade("fiber")
        elif emit.name == "shop_iron":
            comp = self.get_comp("shop_iron")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("iron")
        elif emit.name == "shop_iron_upgrade":
            comp = self.get_comp("shop_iron_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.production_upgrade("iron")
        elif emit.name == "shop_steel":
            comp = self.get_comp("shop_steel")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("steel")
        elif emit.name == "shop_steel_upgrade":
            comp = self.get_comp("shop_steel_upgrade")
            component_shop_update_cost(comp, 3)
            self.game_data.production_upgrade("steel")
        elif emit.name == "shop_mouse":
            comp = self.get_comp("shop_mouse")
            component_shop_update_cost(comp, 2)
            self.game_data.click_fiber *= 2
            self.game_data.cost_fiber = int(round(self.game_data.cost_fiber * 1.9))
            self.game_data.click_iron *= 2
            self.game_data.cost_iron = int(round(self.game_data.cost_iron * 1.9))

    def update(self, dt: float) -> None:
        super().update(dt)

        self.get_comp("resource_wood").change_text(int_smart_str(self.game_data.resource_get("wood")))
        self.get_comp("resource_stone").change_text(int_smart_str(self.game_data.resource_get("stone")))
        self.get_comp("resource_iron").change_text(int_smart_str(self.game_data.resource_get("iron")))
        self.get_comp("resource_fiber").change_text(int_smart_str(self.game_data.resource_get("fiber")))
        self.get_comp("resource_steel").change_text(int_smart_str(self.game_data.resource_get("steel")))
        self.get_comp("resource_kills").change_text(int_smart_str(self.game_data.resource_get("kills")))

        self.get_comp("click_fiber").change_text("-" + int_smart_str(self.game_data.cost_fiber) + "|+" + int_smart_str(self.game_data.click_fiber))
        self.get_comp("click_iron").change_text("-" + int_smart_str(self.game_data.cost_iron) + "|+" + int_smart_str(self.game_data.click_iron))

class SceneGameBattle(SceneGameBase):
    def __init__(self) -> None:
        super().__init__("game_battle")

    def create(self) -> None:
        # BG
        self.new_comp(Image(0, 0, 1, img_path("Bg//forest.png"), False))

        # CLICKERS
        x = 0.52
        def elements_click(self):
            self.emit.append(Emit("take_elements", []))
        self.new_comp(ButtonImage(x, 0.5, 0.4, img_path("Game\\elementals.png"), elements_click))
        self.new_comp(Text(x, 0.5, 0.1, "1000000"), "click_elements")

        # EXTRA PANEL
        self.new_comp(Image(0.58, 0.2, 0.9, IMAGE_EXTRA_PANEL, False))
        x, y, spacing = 0.6, 0.28, 0.032
        self.new_comp(Image(x, y, 0.1, IMAGE_ICON_WOOD, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing, y, 0.07, "1 000 000", (64, 41, 40)), "resource_wood")
        self.new_comp(Image(x + spacing * 2, y, 0.1, IMAGE_ICON_STONE, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 3, y, 0.07, "1 000 000", (64, 41, 40)), "resource_stone")
        self.new_comp(Image(x + spacing * 4, y, 0.1, IMAGE_ICON_FIBER, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 5, y, 0.07, "1 000 000", (64, 41, 40)), "resource_iron")
        self.new_comp(Image(x + spacing * 6, y, 0.1, IMAGE_ICON_IRON, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 7, y, 0.07, "1 000 000", (64, 41, 40)), "resource_fiber")
        self.new_comp(Image(x + spacing * 8, y, 0.1, IMAGE_ICON_KILLS, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 9, y, 0.07, "1 000 000", (64, 41, 40)), "resource_kills")
        self.new_comp(Image(x + spacing * 10, y, 0.1, IMAGE_ICON_ELEMENTS, color=(0, 0, 0, 255)))
        self.new_comp(Text(x + spacing * 11, y, 0.07, "1 000 000", (64, 41, 40)), "resource_elements")
        # EXTRA PANEL BUTTONS
        size = 0.15
        x, y = 0.59, 0.36
        # elements
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\elements.png"),["wood", "wood", 10, "stone", "stone", 10], "hello", "shop_elements"), "shop_elements")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\elements_upgrade.png"),["fiber", "fiber", 10, "steel", "steel", 10], "hello", "shop_elements_upgrade", (1, 0)),"shop_elements_upgrade")
        # mouse
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\mouse.png"),["steel", "steel", 10, "skull", "kills", 10], "hello", "shop_mouse", (2, 0)),"shop_mouse")
        # units
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\unit1.png"),["elements", "elements", 10, "wood", "wood", 10], "hello", "shop_unit1", (0, 1)),"shop_unit1")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\unit2.png"),["elements", "elements", 10, "stone", "stone", 10], "hello", "shop_unit2", (1, 1)),"shop_unit2")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\unit3.png"),["elements", "elements", 10, "fiber", "fiber", 10], "hello", "shop_unit3", (0, 2)),"shop_unit3")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\unit4.png"),["elements", "elements", 10, "iron", "iron", 10], "hello", "shop_unit4", (1, 2)),"shop_unit4")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\unit5.png"),["elements", "elements", 10, "steel", "steel", 10], "hello", "shop_unit5", (0, 3)),"shop_unit5")
        self.new_comp(ShopButton(x, y, size, IMAGE_SHOP_BUTTON, img_path("Game\\Shop\\unit6.png"),["elements", "elements", 10, "skull", "kills", 10], "hello", "shop_unit6", (1, 3)),"shop_unit6")

        # battle
        def hover(self, state):
            if state:
                self.change_color((100, 0, 0))
            else:
                self.change_color((200, 0, 0))
        def click(self):
            self.emit.append(Emit("battle_start", []))
        self.new_comp(ButtonText(0.25, 0.5, 0.2, "TO BATTLE", click,(255, 255, 255), hover_func=hover), "battle_button")
        self.new_comp(Text(0.25, 0.7, 0.1, "temp", (0, 0, 0)), "battle_chance")
        self.new_comp(Text(0.25, 0.7, 0.1, "temp", (0, 0, 0)), "battle_timer")

        # SUPER
        super().create()

    def handel_emit(self, emit: Emit):
        super().handel_emit(emit)

        if emit.name == "take_elements":
            self.game_data.resource_add("elements", self.game_data.click_elements)
            self.game_data.stat_add("elements_clicked", self.game_data.click_elements)
        elif emit.name == "shop_elements":
            comp = self.get_comp("shop_elements")
            component_shop_update_cost(comp, 1.5)
            self.game_data.production_build("elements")
        elif emit.name == "shop_elements_upgrade":
            comp = self.get_comp("shop_elements_upgrade")
            component_shop_update_cost(comp, 2)
            self.game_data.production_upgrade("elements")
        elif emit.name == "shop_mouse":
            comp = self.get_comp("shop_mouse")
            component_shop_update_cost(comp, 2)
            self.game_data.click_elements *= 2

        elif emit.name == "shop_unit1":
            comp = self.get_comp("shop_unit1")
            component_shop_update_cost(comp, 1.2)
            self.game_data.battle_power += 1
        elif emit.name == "shop_unit2":
            comp = self.get_comp("shop_unit2")
            component_shop_update_cost(comp, 1.2)
            self.game_data.battle_power += 2
        elif emit.name == "shop_unit3":
            comp = self.get_comp("shop_unit3")
            component_shop_update_cost(comp, 1.2)
            self.game_data.battle_power += 4
        elif emit.name == "shop_unit4":
            comp = self.get_comp("shop_unit4")
            component_shop_update_cost(comp, 1.2)
            self.game_data.battle_power += 8
        elif emit.name == "shop_unit5":
            comp = self.get_comp("shop_unit5")
            component_shop_update_cost(comp, 1.2)
            self.game_data.battle_power += 16
        elif emit.name == "shop_unit6":
            comp = self.get_comp("shop_unit6")
            component_shop_update_cost(comp, 1.2)
            self.game_data.battle_power += 32

        elif emit.name == "battle_start":
            if self.game_data.battle_timer == -1:
                if self.get_comp("battle_button").text_content == "TO BATTLE":
                    self.get_comp("battle_button").change_text("IN BATTLE")
                    self.game_data.battle_timer = 15
                    self.game_data.battle_current_chance = self.game_data.battle_power / self.game_data.battle_targets
                else:
                    self.get_comp("battle_button").change_text("TO BATTLE")

    def update(self, dt: float) -> None:
        super().update(dt)

        self.get_comp("resource_wood").change_text(int_smart_str(self.game_data.resource_get("wood")))
        self.get_comp("resource_stone").change_text(int_smart_str(self.game_data.resource_get("stone")))
        self.get_comp("resource_iron").change_text(int_smart_str(self.game_data.resource_get("iron")))
        self.get_comp("resource_fiber").change_text(int_smart_str(self.game_data.resource_get("fiber")))
        self.get_comp("resource_kills").change_text(int_smart_str(self.game_data.resource_get("kills")))
        self.get_comp("resource_elements").change_text(int_smart_str(self.game_data.resource_get("elements")))

        self.get_comp("click_elements").change_text("+" + int_smart_str(self.game_data.click_elements))


        if self.game_data.battle_timer == -1:
            self.get_comp("battle_chance").change_text("Success chance : " + str(int((self.game_data.battle_power / self.game_data.battle_targets) * 100)) + "/100")
            self.get_comp("battle_timer").change_text("")
        else:
            self.get_comp("battle_chance").change_text("")
            self.get_comp("battle_timer").change_text("Time left : " + str(int(self.game_data.battle_timer)) + " S")

        if self.game_data.battle_last != -1:
            if self.game_data.battle_last == 0:
                self.get_comp("battle_button").change_text("You Lost")
            else:
                self.get_comp("battle_button").change_text("You Won")
            self.game_data.battle_last = -1

class SceneGameAscend(SceneGameBase):
    def __init__(self) -> None:
        super().__init__("game_ascend")

    def create(self) -> None:
        # BG
        self.new_comp(Image(0, 0, 1, img_path("Bg//gold.png"), False))

        # EXTRA PANEL
        self.new_comp(Image(0.58, 0.2, 0.9, IMAGE_EXTRA_PANEL, False))
        self.new_comp(Text(0.59, 0.4, 0.1, "From population :", (0, 0, 0, 255), False))
        self.new_comp(Text(0.59, 0.5, 0.1, "From resources :", (0, 0, 0, 255), False))
        self.new_comp(Text(0.59, 0.6, 0.1, "From buildings :", (0, 0, 0, 255), False))
        self.new_comp(Text(0.59, 0.7, 0.1, "From battles :", (0, 0, 0, 255), False))
        self.new_comp(Text(0.59, 0.8, 0.1, "Combined :", (0, 0, 0, 255), False))

        self.new_comp(Text(0.85, 0.4, 0.1, "temp", (0, 0, 0, 255), False), "population")
        self.new_comp(Text(0.85, 0.5, 0.1, "temp", (0, 0, 0, 255), False), "resources")
        self.new_comp(Text(0.85, 0.6, 0.1, "temp", (0, 0, 0, 255), False), "buildings")
        self.new_comp(Text(0.85, 0.7, 0.1, "temp", (0, 0, 0, 255), False), "battle")
        self.new_comp(Text(0.85, 0.8, 0.1, "temp", (0, 0, 0, 255), False), "combined")

        def hover(self, state):
            if state:
                self.change_color((255, 255, 255))
            else:
                self.change_color((0, 0, 0))
        def click(self):
            self.emit.append(Emit("ascend", []))
        self.new_comp(ButtonText(0.25, 0.5, 0.2, "ASCEND", click, (255, 255, 255), hover_func=hover),"ascend_button")

        # SUPER
        super().create()

    def handel_emit(self, emit: Emit):
        super().handel_emit(emit)

        if emit.name == "ascend":
            self.game_data.ascend_now()
            self.scene_manager_link.switch_scene("game_build")
            self.scene_manager_link.shop_cost_reset()

    def update(self, dt: float) -> None:
        super().update(dt)

        #resources
        #buildings
        #battle

        self.get_comp("population").change_text(str(self.game_data.ascention_get("po")))
        self.get_comp("resources").change_text(str(self.game_data.ascention_get("re")))
        self.get_comp("buildings").change_text(str(self.game_data.ascention_get("bu")))
        self.get_comp("battle").change_text(str(self.game_data.ascention_get("ba")))
        self.get_comp("combined").change_text(str(self.game_data.ascention_get("all")))

class SceneGameStats(SceneGameBase):
    def __init__(self) -> None:
        super().__init__("game_stats")

    def create(self) -> None:
        # BG
        self.new_comp(Image(0, 0, 1, img_path("Bg//sand.png"), False))

        # RESOURCES CLICKED
        x, y, size  = 0.1, 0.2, 0.08
        spacing = size
        self.new_comp(Text(x, y, 0.12, "Clicked :", (0, 0, 0), False))
        self.new_comp(Text(x, y + spacing * 2, size, "temp", (0, 0, 0), False), "clicked_wood")
        self.new_comp(Text(x, y + spacing * 3, size, "temp", (0, 0, 0), False), "clicked_stone")
        self.new_comp(Text(x, y + spacing * 4, size, "temp", (0, 0, 0), False), "clicked_fiber")
        self.new_comp(Text(x, y + spacing * 5, size, "temp", (0, 0, 0), False), "clicked_iron")
        self.new_comp(Text(x, y + spacing * 6, size, "temp", (0, 0, 0), False), "clicked_food")
        self.new_comp(Text(x, y + spacing * 7, size, "temp", (0, 0, 0), False), "clicked_elements")

        # RESOURCES GATHERED
        x, y, size = 0.4, 0.2, 0.08
        spacing = size
        self.new_comp(Text(x, y, 0.12, "Gathered :", (0, 0, 0), False))
        self.new_comp(Text(x, y + spacing * 2, size, "temp", (0, 0, 0), False), "gathered_wood")
        self.new_comp(Text(x, y + spacing * 3, size, "temp", (0, 0, 0), False), "gathered_stone")
        self.new_comp(Text(x, y + spacing * 4, size, "temp", (0, 0, 0), False), "gathered_fiber")
        self.new_comp(Text(x, y + spacing * 5, size, "temp", (0, 0, 0), False), "gathered_iron")
        self.new_comp(Text(x, y + spacing * 6, size, "temp", (0, 0, 0), False), "gathered_food")
        self.new_comp(Text(x, y + spacing * 7, size, "temp", (0, 0, 0), False), "gathered_elements")
        self.new_comp(Text(x, y + spacing * 8, size, "temp", (0, 0, 0), False), "gathered_steel")

        # BUILDINGS BUILD
        x, y, size = 0.7, 0.2, 0.08
        spacing = size
        self.new_comp(Text(x, y, 0.12, "Build :", (0, 0, 0), False))
        self.new_comp(Text(x, y + spacing * 2, size, "temp", (0, 0, 0), False), "built_wood")
        self.new_comp(Text(x, y + spacing * 3, size, "temp", (0, 0, 0), False), "built_stone")
        self.new_comp(Text(x, y + spacing * 4, size, "temp", (0, 0, 0), False), "built_fiber")
        self.new_comp(Text(x, y + spacing * 5, size, "temp", (0, 0, 0), False), "built_iron")
        self.new_comp(Text(x, y + spacing * 6, size, "temp", (0, 0, 0), False), "built_food")
        self.new_comp(Text(x, y + spacing * 7, size, "temp", (0, 0, 0), False), "built_elements")
        self.new_comp(Text(x, y + spacing * 8, size, "temp", (0, 0, 0), False), "built_steel")

        # SUPER
        super().create()

    def update(self, dt: float) -> None:
        super().update(dt)

        self.get_comp("clicked_wood").change_text("Wood : " + int_smart_str(self.game_data.stat_get("wood_clicked")))
        self.get_comp("clicked_stone").change_text("Stone : " + int_smart_str(self.game_data.stat_get("stone_clicked")))
        self.get_comp("clicked_fiber").change_text("Fiber : " + int_smart_str(self.game_data.stat_get("fiber_clicked")))
        self.get_comp("clicked_iron").change_text("Iron : " + int_smart_str(self.game_data.stat_get("iron_clicked")))
        self.get_comp("clicked_food").change_text("Food  : " + int_smart_str(self.game_data.stat_get("food_gathered")))
        self.get_comp("clicked_elements").change_text("Elements : " + int_smart_str(self.game_data.stat_get("elements_clicked")))

        self.get_comp("gathered_wood").change_text("Wood : " + int_smart_str(self.game_data.stat_get("wood_gathered")))
        self.get_comp("gathered_stone").change_text("Stone : " + int_smart_str(self.game_data.stat_get("stone_gathered")))
        self.get_comp("gathered_fiber").change_text("Fiber : " + int_smart_str(self.game_data.stat_get("fiber_gathered")))
        self.get_comp("gathered_iron").change_text("Iron : " + int_smart_str(self.game_data.stat_get("iron_gathered")))
        self.get_comp("gathered_food").change_text("Food : " + int_smart_str(self.game_data.stat_get("food_gathered")))
        self.get_comp("gathered_elements").change_text("Elements : " + int_smart_str(self.game_data.stat_get("elements_gathered")))
        self.get_comp("gathered_steel").change_text("Steel : " + int_smart_str(self.game_data.stat_get("steel_gathered")))

        self.get_comp("built_wood").change_text("Wood : " + int_smart_str(self.game_data.production["wood"][1]))
        self.get_comp("built_stone").change_text("Stone : " + int_smart_str(self.game_data.production["stone"][1]))
        self.get_comp("built_fiber").change_text("Fiber : " + int_smart_str(self.game_data.production["fiber"][1]))
        self.get_comp("built_iron").change_text("Iron : " + int_smart_str(self.game_data.production["iron"][1]))
        self.get_comp("built_food").change_text("Food : " + int_smart_str(self.game_data.production["food"][1]))
        self.get_comp("built_elements").change_text("Elements : " + int_smart_str(self.game_data.production["elements"][1]))
        self.get_comp("built_steel").change_text("Steel : " + int_smart_str(self.game_data.production["steel"][1]))


########################################################### MANAGERS
class SceneManager:
    """manages all the scenes"""
    def __init__(self) -> None:
        self.scene_current  : callable      = None
        self.scenes         : dict[str:any] = {}
        self.history        : list[callable] = []

        self.create()
        self.switch_scene("main_menu", False)

    def draw(self, surface_target: Surface) -> None:
        self.scene_current.draw(surface_target)

    def update(self, dt: float) -> None:
        self.scene_current.update(dt)

    def initialize(self, screen_size: tuple[int, int], game_data: GameData) -> None:
        for scene in self.scenes.values():
            scene.initialize(screen_size, self, game_data)

    def handle_key(self, key: str) -> None:
        self.scene_current.handle_key(key)

    def shop_cost_reset(self):
        for scene in self.scenes.values():
            scene.component_manager.shop_cost_reset()

    def handle_muse(self, button: int) -> None:
        self.scene_current.handle_mouse(button)

    def switch_scene(self, scene_name: str, n_skip: bool = True) -> None:
        if scene_name in self.scenes.keys():
            if n_skip:
                self.history.append(self.scene_current)
                if len(self.history) > 100:
                    self.history.pop(0)

            self.scene_current = self.scenes[scene_name]
            self.scene_current.on_scene_switch()

    def back_track(self):
        if len(self.history) != 0:
            try:
                self.scene_current.game_data
                self.scene_current.get_comp("AnimTransition").emit.append(Emit("BeginTransition", [self.history[-1].name, False]))
            except AttributeError:
                self.switch_scene(self.history[-1].name, False)
            self.history.pop(-1)

    def history_add_self(self):
        self.history.append(self.scene_current)
        if len(self.history) > 100:
            self.history.pop(0)

    def create(self) -> None:
        # MAIN MENU
        self.scenes.update({"main_menu": SceneMainMenu()})

        # SETTINGS
        self.scenes.update({"settings": SceneSettings()})

        # Game Main
        self.scenes.update({"game_build": SceneGameBuild()})
        self.scenes.update({"game_work": SceneGameWork()})
        self.scenes.update({"game_battle": SceneGameBattle()})
        self.scenes.update({"game_ascend": SceneGameAscend()})
        self.scenes.update({"game_stats": SceneGameStats()})

class ComponentManager:
    """manages all the components in a scene"""
    def __init__(self) -> None:
        self.WINDOW_SIZE   = None
        self.surface       = None

        self.components : dict[str:Component]   = {}
        self.remove_que : list[str]             = []

        self.scene_link = None

    def initialize(self, screen_size: tuple[int, int], scene_link: SceneBase, game_data: GameData = None) -> None:
        self.WINDOW_SIZE    : tuple[int, int]   = screen_size
        self.surface        : Surface           = Surface(self.WINDOW_SIZE)
        self.scene_link     : SceneBase         = scene_link

        for component in self.components.values():
            if component.__class__.__name__ == "ShopButton":
                component.initialize(self.WINDOW_SIZE, self, game_data)
            else:
                component.initialize(self.WINDOW_SIZE, self)

    def draw(self, surface_target: Surface) -> None:
        self.surface.fill((0, 0, 0), [0, 0, self.WINDOW_SIZE[0], self.WINDOW_SIZE[1]])

        for component in self.components.values():
            self.surface.blit(component.surface, component.position)

        surface_target.blit(self.surface, (0, 0))

    def update(self, dt: float) -> None:
        for component in self.components.values():
            # update
            component.update(dt)

            # emit
            if component.emit:
                for emit in component.emit:
                    self.scene_link.scene_manager_link.scene_current.handel_emit(emit)
            component.emit = []

        self.remove_action()

    def shop_cost_reset(self):
        for comp in self.components.values():
            if comp.__class__.__name__ == "ShopButton":
                comp.reset()

    def handle_mouse(self, button: int) -> None:
        for component in self.components.values():
            if "button" in component.tags:
                component.check_click(button)

    def new_component(self, component: Component, comp_id: str = "") -> None:
        if comp_id:
            self.components.update({comp_id: component})
        else:
            keys = list(self.components.keys())
            next_number = 0

            while True:
                temp_next_number = randint(1000, 9999)
                if temp_next_number not in keys:
                    next_number = temp_next_number
                    break

            self.components.update({str(next_number): component})

    def get_component(self, comp_id: str) -> Component:
        return self.components[comp_id]

    def remove(self, comp_id: str):
        if comp_id not in self.remove_que:
            self.remove_que.append(comp_id)

    def remove_action(self):
        if len(self.remove_que):
            for comp_id in self.remove_que:
                self.components.pop(comp_id)
                self.remove_que.remove(comp_id)