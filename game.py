import time
import numpy as np
from events import Orbit, EventHandler, ActiveManager
from sprite import Fruit, FruitCut, Circle, Boom
from tools import pw, ph, q_exit, scale, get_hit_k, load_image, Music, Mark, Score, abs_path
import random
import pygame


class Game:
    def __init__(self):
        pygame.init()

        # 屏幕初始化
        clock = pygame.time.Clock()
        self.fps_control = lambda: clock.tick(60)  # 帧率控制
        self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)  # 全屏显示
        self.music = Music()
        self.imgs = load_image()
        pygame.display.set_caption("手指水果忍者")
        pygame.display.set_icon(self.imgs["icon"])
        self.background = pygame.transform.scale(self.imgs["background"], (pw(1), ph(1)))

        # 事件注册
        self.event_handler = EventHandler()
        self.orbit = Orbit(self.screen)
        self.event_handler.register_callback(self.orbit.push)  # 为鼠标轨迹生成器注册回调事件
        self.active_manager = ActiveManager()
        self.event_handler.register_callback(self.active_manager.push)  # 为窗口活动跟踪器注册回调事件

        self.game_run()

    def game_run(self):  # 游戏过程控制
        page_map = {"home": self.home_page, "play": self.game_page, "over": self.game_over, "quit": q_exit, "rank": self.rank_page }
        action = "home"
        args = []
        while 1:
            print(action, args)
            action, args = page_map[action](*args)

    def rank_page(self):
        # TODO 排行榜页面
        pass

    def game_over(self, surface, sprites, rect):  # 游戏结束
        sprite_group = pygame.sprite.Group(*sprites)
        for i in sprite_group:
            if isinstance(i, Fruit) or isinstance(i, Boom):
                i.sprite_grop = sprite_group

        # 生成非线性动画
        deg = np.arange(0, 93, 3)
        line = np.sin(deg * np.pi / 180)
        step_1 = surface.copy()
        if rect:
            sprite_group.remove(*[i for i in sprites if isinstance(i, Circle)])
            circle_group = pygame.sprite.Group()
            for i in range(100):
                self.fps_control()
                self.screen.blit(step_1, (0, 0))
                for _ in range(30):
                    circle_group.add(Circle((242, 191, 91 + i), rect.left, rect.top, i / 5))
                circle_group.update()
                sprite_group.draw(self.screen)
                circle_group.draw(self.screen)
                self.event_handler.load_event()
                self.orbit.draw()
                pygame.display.flip()

            [i.kill() for i in sprite_group]
            surface = pygame.Surface([pw(1), pw(1)]).convert_alpha()
            surface.fill((255, 255, 255), (0, 0, pw(1), ph(1)))

            for i in range(3):
                self.fps_control()
                self.screen.blit(step_1, (0, 0))
                surface.set_alpha(i * 85)
                self.screen.blit(surface, (0, 0))
                pygame.display.flip()

            for i in range(30):
                self.fps_control()
                self.screen.blit(step_1, (0, 0))
                self.screen.fill((255, 255, 255), (0, 0, pw(1), ph(1)))
                pygame.display.flip()

            for i in range(60):
                self.fps_control()
                self.screen.blit(step_1, (0, 0))
                surface.set_alpha(int(255 - i * 4.25))
                self.screen.blit(surface, (0, 0))
                pygame.display.flip()
            self.music.play("over")
        else:
            self.music.play("over")

        for i in line:
            self.fps_control()
            self.screen.blit(step_1, (0, 0))
            sprite_group.update()
            sprite_group.draw(self.screen)
            tmp = scale((pw(0.8), ph(0.4)), (pw(0.1), ph(0.3)), i)
            self.screen.blit(pygame.transform.scale(self.imgs["game-over"], tmp[0]), tmp[1])
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()

        for i in range(180):
            self.fps_control()
            self.screen.blit(step_1, (0, 0))
            sprite_group.update()
            sprite_group.draw(self.screen)
            tmp = scale((pw(0.8), ph(0.4)), (pw(0.1), ph(0.3)), 1)
            self.screen.blit(pygame.transform.scale(self.imgs["game-over"], tmp[0]), tmp[1])
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()
        while 1:
            time.sleep(0.1)
            self.event_handler.load_event()
            if self.active_manager.active:
                break
        return "home", []

    def game_page(self, k):  # 游戏过程
        sprite_group = pygame.sprite.Group()
        return_message = []
        score = Score()

        def game_over_callback(rect=None):
            return_message.append(rect)

        self.music.game()
        self.music.play("start")
        sprite_group.add(FruitCut("sandia-1", pw(0.552), ph(0.502), -200, k, self.imgs))
        sprite_group.add(FruitCut("sandia-2", pw(0.552), ph(0.502), 200, k, self.imgs))
        for i in range(20):
            sprite_group.add(Circle((88, 135, 15), pw(0.552), ph(0.617), 2))

        self.screen.blit(self.background, (0, 0))
        # 生成非线性动画
        deg = np.arange(0, 93, 3)
        line = np.sin(deg * np.pi / 180)
        for i in 1 - line:
            self.fps_control()
            self.event_handler.load_event()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(
                pygame.transform.scale(self.imgs["xxx"], (pw(0.06), ph(0.08))), (pw(0.94) + i * pw(0.06), ph(0.01))
            )
            self.screen.blit(
                pygame.transform.scale(self.imgs["xx"], (pw(0.04), ph(0.065))), (pw(0.9) + i * pw(0.1), ph(0.01))
            )
            self.screen.blit(
                pygame.transform.scale(self.imgs["x"], (pw(0.035), ph(0.05))), (pw(0.865) + i * pw(0.135), ph(0.01))
            )
            self.screen.blit(
                pygame.transform.scale(self.imgs["score"], (pw(0.06), ph(0.08))), (pw(0.01) - i * pw(0.05), ph(0.01))
            )
            self.screen.blit(score.text_surface, (pw(0.07) - i * pw(0.1), pw(0.01)))
            sprite_group.update()
            sprite_group.draw(self.screen)
            self.orbit.draw()
            pygame.display.flip()

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["xxx"], (pw(0.06), ph(0.08))), (pw(0.94), ph(0.01)))
        self.screen.blit(pygame.transform.scale(self.imgs["xx"], (pw(0.04), ph(0.065))), (pw(0.9), ph(0.01)))
        self.screen.blit(pygame.transform.scale(self.imgs["x"], (pw(0.035), ph(0.05))), (pw(0.865), ph(0.01)))
        self.screen.blit(pygame.transform.scale(self.imgs["score"], (pw(0.06), ph(0.08))), (pw(0.01), ph(0.01)))
        pygame.display.flip()
        step_1 = self.screen.copy()

        index = 0
        mark = Mark(step_1, self.screen, self.imgs, game_over_callback)
        while 1:
            if return_message:
                self.screen.blit(step_1, (0, 0))
                self.screen.blit(score.text_surface, (pw(0.07), pw(0.01)))
                return "over", (self.screen, sprite_group, return_message[0])
            index += 1
            self.fps_control()
            self.screen.blit(step_1, (0, 0))
            self.screen.blit(score.text_surface, (pw(0.07), pw(0.01)))
            if index % 30 == 0 and random.random() > 0.5:
                sprite_group.add(Fruit(mark.post, self.imgs, self.music, sprite_group, self.orbit, score.add))
                self.music.play("throw")
            if index % 60 == 0 and random.random() > 0.8:
                sprite_group.add(Boom(self.imgs, self.music, sprite_group, self.orbit, game_over_callback))
                self.music.play("throw")

            sprite_group.update()
            sprite_group.draw(self.screen)
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()

    def home_page(self):  # 主页
        self.music.menu()

        # 生成上侧加载动画
        deg = np.arange(0, 93, 3)
        line = np.sin(deg * np.pi / 180)
        for i in line - 1:
            self.fps_control()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(pygame.transform.scale(self.imgs["home-mask"], (pw(1), ph(0.4))), (0, i * ph(0.4)))
            self.screen.blit(
                pygame.transform.scale(self.imgs["logo"], (pw(0.5), ph(0.3))), (i * pw(0.1) + pw(0.025), i * ph(0.3))
            )
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["home-mask"], (pw(1), ph(0.4))), (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["logo"], (pw(0.5), ph(0.3))), (pw(0.025), 0))
        step_1 = self.screen.copy()

        g = 40.81  # 重力加速度
        dt = 0.016  # 时间步长
        h = 1.0  # 初始高度
        t = 0  # 初始时间
        v = 0  # 初始速度
        heights = []  # 高度数组
        while t < 1:  # 模拟 1 秒钟的时间
            heights.append(h)
            v -= g * dt
            h += v * dt
            t += dt
            if h <= 0:
                h = 0
                v = (0 - v) * 0.7
        for height in heights:
            self.fps_control()
            self.screen.blit(step_1, (0, 0))
            self.screen.blit(
                pygame.transform.scale(self.imgs["ninja"], (pw(0.33), ph(0.15))),
                (pw(0.55), ph(0.1) - ph(0.15) * height),
            )
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()
        self.screen.blit(step_1, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["ninja"], (pw(0.33), ph(0.15))), (pw(0.55), ph(0.1)))
        step_2 = self.screen.copy()

        for i in line - 1:
            self.fps_control()
            self.screen.blit(step_2, (0, 0))
            self.screen.blit(pygame.transform.scale(self.imgs["home-desc"], (pw(0.2), ph(0.2))), (i * pw(0.1), ph(0.3)))
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()
        self.screen.blit(step_2, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["home-desc"], (pw(0.2), ph(0.2))), (0, ph(0.3)))
        step_3 = self.screen.copy()

        # 生成下侧加载动画
        names = ["dojo", "new-game", "quit", "peach", "sandia", "boom"]
        sizes = [
            (pw(0.2), ph(0.3)),
            (pw(0.3), ph(0.45)),
            (pw(0.17), ph(0.25)),
            (pw(0.07), ph(0.12)),
            (pw(0.15), ph(0.22)),
            (pw(0.081), ph(0.108)),
        ]
        dests = [
            (pw(0.1), ph(0.5)),
            (pw(0.4), ph(0.4)),
            (pw(0.75), ph(0.6)),
            (pw(0.17), ph(0.588)),
            (pw(0.477), ph(0.515)),
            (pw(0.795), ph(0.675)),
        ]
        for i in line:
            self.fps_control()
            self.screen.blit(step_3, (0, 0))
            for name, size, dest in zip(names, sizes, dests):
                wh, xy = scale(size, dest, i)
                self.screen.blit(pygame.transform.scale(self.imgs[name], wh), xy)
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()

        sprite_group = pygame.sprite.Group()
        while 1:
            for i in np.arange(0, 360, 1):
                # 旋转动画
                self.fps_control()
                self.screen.blit(step_3, (0, 0))
                for name, size, dest in zip(names, sizes, dests):
                    wh, xy = scale(size, dest, 1)
                    self.screen.blit(pygame.transform.scale(pygame.transform.rotate(self.imgs[name], i), wh), xy)
                if random.random() > 0.8:
                    angle_rad = np.radians((i + 120) % 360)
                    x = 0.835 + 0.055 * np.cos(angle_rad)
                    y = 0.73 - 0.055 * np.sin(angle_rad)
                    sprite_group.add(Circle((242, 191, 98), pw(x), ph(y), 0.5))
                sprite_group.draw(self.screen)
                sprite_group.update()

                self.event_handler.load_event()
                self.orbit.draw()

                # 点击事件
                k = get_hit_k(pygame.Rect((pw(0.15), ph(0.58)), (pw(0.1), ph(0.15))), self.orbit)
                if k:
                    self.music.play("splatter")
                    return "rank", []
                k = get_hit_k(pygame.Rect((pw(0.477), ph(0.507)), (pw(0.15), ph(0.22))), self.orbit)
                if k:
                    self.music.play("splatter")
                    return "play", [k]
                k = get_hit_k(pygame.Rect((pw(0.78), ph(0.68)), (pw(0.12), ph(0.05))), self.orbit)
                if k:
                    self.music.play("splatter")
                    for _ in range(20):
                        self.fps_control()
                        self.event_handler.load_event()
                        self.orbit.draw()
                        pygame.display.flip()
                    return "quit", []

                pygame.display.flip()
