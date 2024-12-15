import os
import string
import time
import numpy as np
from events import Orbit, EventHandler, ActiveManager
from sprite import Fruit, FruitCut, Circle, Boom
from tools import pw, ph, q_exit, save_score,load_score, scale, get_hit_k, load_image, Music, Mark, Score, abs_path
import random
import pygame


class Game:
    def __init__(self):
        pygame.init()

        # 屏幕初始化
        clock = pygame.time.Clock()
        self.fps_control = lambda: clock.tick(60)  # 帧率控制
        # self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)  # 全屏显示
        self.screen = pygame.display.set_mode((pw(1), ph(1)), flags=pygame.RESIZABLE)  # 窗口显示
        self.music = Music()
        self.imgs = load_image()
        pygame.display.set_caption("手指水果忍者")
        pygame.display.set_icon(self.imgs["icon"])
        self.background = pygame.transform.scale(self.imgs["background"], (pw(1), ph(1)))

        # 事件注册
        self.event_handler = EventHandler(self)
        self.orbit = Orbit(self.screen)
        self.event_handler.register_callback(self.orbit.push)  # 为鼠标轨迹生成器注册回调事件
        self.active_manager = ActiveManager()
        self.event_handler.register_callback(self.active_manager.push)  # 为窗口活动跟踪器注册回调事件

        self.game_run()

    def game_run(self):  # 游戏过程控制
        page_map = {
            "home": self.home_page,
            "play": self.game_page,
            "over": self.game_over,
            "quit": q_exit,
            "save": self.save_page,
            "rank": self.rank_page,
        }
        action = "home"
        args = []
        while 1:
            print(action, args)
            action, args = page_map[action](*args)

    def draw_leaderboard(self):
        
        # 加载资源
        border_color = (255, 255, 255)  # 白色边框
        title_font = pygame.font.Font(None, 64)
        text_font = pygame.font.Font(None, 36)
        border_color = (0, 255, 255)  # 边框为青色border_color = (0, 255, 255)  # 边框为青色
        title_color = (255, 215, 0)  # 标题为金色
        text_color = (255, 215, 0)  # 正常文本为白色
        highlight_color = (255, 215, 0)  # 高亮的名字为金色
        divider_color = (100, 100, 100)  # 分割线颜色为灰色

        if os.path.isfile("./scores.sav"):
            leaderboard = load_score()
        else:
            leaderboard = []

        # 示例排行榜数据
        '''
        leaderboard = [
            {"name": "Alice", "score": 150},
            {"name": "Bob", "score": 120},
            {"name": "Charlie", "score": 100},
            {"name": "Dave", "score": 90},
            {"name": "Eve", "score": 80},
        ]
        '''
        # 填充背景色
        #self.screen.fill(background_color)
        # 计算排行榜窗口的大小
        leaderboard_width = 600
        leaderboard_height = 500
        # 居中计算
        window_x = (self.screen.get_width() - leaderboard_width) // 2
        window_y = (self.screen.get_height() - leaderboard_height) // 2 + 90

        # 绘制整体边框
        pygame.draw.rect(self.screen, border_color, (window_x, window_y, leaderboard_width, leaderboard_height), 5)
        
        # 绘制标题
        title = title_font.render("Leaderboard", True, title_color)
        self.screen.blit(title, (window_x + 180, window_y +40))
        
        # 绘制分割线
        pygame.draw.line(self.screen, divider_color, (window_x + 50, window_y + 120), (window_x + 550, window_y + 120), 2)

        # 绘制排行榜条目
        for i, entry in enumerate(leaderboard):
            y_pos = window_y + 140 + i * 50  # 每个条目的垂直间距
            name = entry['username']
            score = entry['score']
            text_color = (255, 255, 255)
            
            # 显示排名
            rank_surface = text_font.render(f"{i + 1}.", True, text_color)
            self.screen.blit(rank_surface, (window_x + 70, y_pos))
            
            # 显示玩家名字
            name_surface = text_font.render(name, True, text_color)
            self.screen.blit(name_surface, (window_x + 140, y_pos))
            
            # 显示分数
            score_surface = text_font.render(str(score), True, text_color)
            self.screen.blit(score_surface, (window_x + 450, y_pos))
        
        # 绘制底部装饰
        pygame.draw.line(self.screen, divider_color,  (window_x + 50, window_y + 500), (window_x + 550, window_y + 500), 2)
        

    def rank_page(self):
        sprite_group = pygame.sprite.Group()
        self.music.menu()
        # 生成非线性动画
        deg = np.arange(0, 93, 3)
        line = np.sin(deg * np.pi / 180)
        '''
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
        '''
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["home-mask"], (pw(1), ph(0.4))), (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["logo"], (pw(0.5), ph(0.3))), (pw(0.025), 0))
        step_1 = self.screen.copy()
        
        # 生成非线性动画
        g = 40.81  # 重力加速度
        dt = 0.016  # 时间步长

        h = 1.0  # 初始高度
        t = 0  # 初始时间
        v = 0  # 初始速度
        heights = []  # 高度数组

        while t < 1:  # 模拟10秒钟的时间
            heights.append(h)
            v -= g * dt
            h += v * dt
            t += dt
            if h <= 0:
                h = 0
                v = (0 - v) * 0.7

        '''
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
        '''
        self.screen.blit(step_1, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["ninja"], (pw(0.33), ph(0.15))), (pw(0.55), ph(0.1)))
        step_2 = self.screen.copy()

        '''
        for i in line - 1:
            self.fps_control()
            self.screen.blit(step_2, (0, 0))
            self.screen.blit(pygame.transform.scale(self.imgs["home-desc"], (pw(0.2), ph(0.2))), (i * pw(0.1), ph(0.3)))
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()
        self.screen.blit(step_2, (0, 0))
        self.screen.blit(pygame.transform.scale(self.imgs["home-desc"], (pw(0.2), ph(0.2))), (0, ph(0.3)))
        '''
        step_3 = self.screen.copy()

        for i in line:
            self.fps_control()
            self.screen.blit(step_3, (0, 0))
            tmp = scale((pw(0.1), ph(0.15)), (pw(0.05), ph(0.77)), i)
            self.screen.blit(pygame.transform.scale(self.imgs["dojo"], tmp[0]), tmp[1])

            tmp = scale((pw(0.035), ph(0.06)), (pw(0.0846), ph(0.816)), i)
            self.screen.blit(pygame.transform.scale(self.imgs["peach"], tmp[0]), tmp[1])

            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()

        step_4 = self.screen.copy()
        self.draw_leaderboard()
        pygame.display.flip()

        while 1:
            for i in np.arange(0, 360, 1):
                self.fps_control()
                self.screen.blit(step_3, (0, 0))
                tmp = scale((pw(0.1), ph(0.15)), (pw(0.05), ph(0.77)), 1)
                self.screen.blit(pygame.transform.scale(pygame.transform.rotate(self.imgs["dojo"], i), tmp[0]), tmp[1])
                tmp = scale((pw(0.035), ph(0.06)), (pw(0.0846), ph(0.816)), 1)
                self.screen.blit(pygame.transform.scale(pygame.transform.rotate(self.imgs["peach"], i), tmp[0]), tmp[1])

                #if random.random() > 0.8:
                #    sprite_group.add(Circle((242, 191, 98), pw(0.785), ph(0.65), 0.5))
                sprite_group.draw(self.screen)
                sprite_group.update()

                self.event_handler.load_event()
                self.orbit.draw()
                #k = get_hit_k(pygame.Rect((pw(0.15), ph(0.58)), (pw(0.1), ph(0.15))), self.orbit)
                k = get_hit_k(pygame.Rect((pw(0.06), ph(0.75)), (pw(0.05), ph(0.05))), self.orbit)
                if k:
                    self.music.play("splatter")
                    return "home", []

    def save_page(self, score):
        active = True
        saved = False
        username = ""
        input_box = pygame.Rect(pw(0.4), ph(0.4), pw(0.2), ph(0.05))
        button = pygame.Rect(pw(0.4), ph(0.5), pw(0.2), ph(0.05))
        font = pygame.font.SysFont(pygame.font.get_fonts()[5], int(ph(0.04)))

        while not saved:
            self.fps_control()
            self.screen.blit(self.background, (0, 0))

            score_text = font.render(f"Score: {score}", True, (210, 113, 20))
            user_text = font.render("Username:", True, (210, 113, 20))
            input_text = font.render(username, True, (0, 0, 0))
            button_text = font.render("Save", True, (210, 113, 20))

            pygame.draw.rect(self.screen, (200, 200, 200), input_box, 0)
            pygame.draw.rect(self.screen, (0, 0, 0) if active else (200, 200, 200), input_box, 2)
            pygame.draw.rect(self.screen, (210, 113, 20), button, 2)
            
            self.screen.blit(score_text, (pw(0.4), ph(0.3)))
            self.screen.blit(user_text, (input_box.x, input_box.y - ph(0.05)))
            self.screen.blit(input_text, (input_box.x + pw(0.005), input_box.y))
            self.screen.blit(button_text, (button.x + pw(0.07), button.y + ph(0.003)))

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                    if button.collidepoint(event.pos):
                        save_score(username, score)
                        saved = True
                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        save_score(username, score)
                        saved = True
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.unicode.isalnum() and len(username) < 10:
                        username += event.unicode
                pygame.event.post(event)
            self.event_handler.load_event()
            self.orbit.draw()
            pygame.display.flip()
        return "home", []

    def game_over(self, surface, sprites, score, rect):  # 游戏结束
        sprite_group = pygame.sprite.Group(*sprites)
        for i in sprite_group:
            if isinstance(i, Fruit) or isinstance(i, Boom):
                i.sprite_grop = sprite_group

        # 炸弹爆炸动画
        deg = np.arange(0, 93, 3)
        line = np.sin(deg * np.pi / 180)
        step_1 = surface.copy()
        if rect:
            # 粒子效果
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

            # 白光效果
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
        
        # gameover 入场动画
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

        # gameover 停留
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
        return "save", [score.score]

    def game_page(self, k):  # 游戏过程
        sprite_group = pygame.sprite.Group()
        return_message = []
        score = Score()

        def game_over_callback(rect=None):
            return_message.append(rect)

        # 开始特效
        self.music.game()
        self.music.play("start")
        sprite_group.add(FruitCut("sandia-1", pw(0.552), ph(0.502), -200, k, self.imgs))
        sprite_group.add(FruitCut("sandia-2", pw(0.552), ph(0.502), 200, k, self.imgs))
        for i in range(20):
            sprite_group.add(Circle((88, 135, 15), pw(0.552), ph(0.617), 2))

        # 顶部图标入场动画
        self.screen.blit(self.background, (0, 0))
        names = ["xxx", "xx", "x", "score"]
        sizes = [(pw(0.06), ph(0.08)), (pw(0.04), ph(0.065)), (pw(0.035), ph(0.05)), (pw(0.06), ph(0.08))]
        dests = [(pw(0.94), ph(0.01)), (pw(0.9), ph(0.01)), (pw(0.865), ph(0.01)), (pw(0.01), ph(0.01))]
        deltas = [pw(0.06), pw(0.1), pw(0.135), -pw(0.05)]
        deg = np.arange(0, 93, 3)
        line = np.sin(deg * np.pi / 180)
        for i in 1 - line:
            self.fps_control()
            self.event_handler.load_event()
            self.screen.blit(self.background, (0, 0))
            for name, size, dest, delta in zip(names, sizes, dests, deltas):
                self.screen.blit(pygame.transform.scale(self.imgs[name], size), (dest[0] + i * delta, dest[1]))
            self.screen.blit(score.text_surface, (pw(0.07) - i * pw(0.1), pw(0.01)))
            sprite_group.update()
            sprite_group.draw(self.screen)
            self.orbit.draw()
            pygame.display.flip()
        self.screen.blit(self.background, (0, 0))
        for name, size, dest in zip(names, sizes, dests):
            self.screen.blit(pygame.transform.scale(self.imgs[name], size), dest)
        pygame.display.flip()
        step_1 = self.screen.copy()

        index = 0
        mark = Mark(step_1, self.screen, self.imgs, game_over_callback)
        while 1:
            if return_message:
                self.screen.blit(step_1, (0, 0))
                self.screen.blit(score.text_surface, (pw(0.07), pw(0.01)))
                return "over", (self.screen, sprite_group, score, return_message[0])
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
