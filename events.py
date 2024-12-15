import pygame
import time
from tools import q_exit, ph


# 全局事件管理类
class EventHandler:
    def __init__(self, game):
        self.push_list = []
        self.game = game

    # 用于注册回调函数
    def register_callback(self, func, *args, **kwargs):
        self.push_list.append((func, args, kwargs))

    # 载入剩余事件
    def load_event(self):
        for a_event in pygame.event.get():
            if a_event.type == pygame.QUIT:
                q_exit()
            if a_event.type == pygame.KEYDOWN:
                if a_event.key == pygame.K_ESCAPE:
                    q_exit()
            # if a_event.type == pygame.VIDEORESIZE:
            #     import tools
            #     tools.sx = a_event.w / tools.screen_x
            #     tools.sy = a_event.h / tools.screen_y
            #     self.game.screen = pygame.display.set_mode((a_event.w, a_event.h), flags=pygame.RESIZABLE)  # 窗口显示
            #     self.game.background = pygame.transform.scale(self.game.imgs["background"], (tools.pw(1), tools.ph(1)))
            #     self.game.orbit = Orbit(self.game.screen)
            #     self.game.orbit.draw()
            #     pygame.display.flip()
            for func, args, kwargs in self.push_list:
                func(a_event, *args, **kwargs)


# 用于跟踪窗口活跃状态
class ActiveManager:
    def __init__(self):
        self.active = True

    def push(self, event):
        if event.type == pygame.ACTIVEEVENT:
            if event.gain:
                self.active = True
            else:
                self.active = False


# 全局鼠标轨迹控制类
class Orbit:
    def __init__(self, screen):
        # self.click = False
        self.click = True
        self.orbit = []
        self.screen = screen

    def push(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.click = True
            self.orbit = []
        elif event.type == pygame.MOUSEBUTTONUP:
            # self.click = False
            self.click = True
        elif event.type == pygame.MOUSEMOTION and self.click:
            self.orbit.append([time.time_ns() / 1000000, event.pos])

    def draw(self):
        now = time.time_ns() / 1000000
        self.orbit = list(filter(lambda x: now - x[0] <= 100, self.orbit))

        for i in range(1, len(self.orbit)):
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                self.orbit[i - 1][1],
                self.orbit[i][1],
                int(ph(0.0003) * (self.orbit[i][0] + 100 - now)),
            )
