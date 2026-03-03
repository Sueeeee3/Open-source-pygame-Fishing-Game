import pygame
import random
from settings import top_bound2, bottom_bound2, WIDTH, HEIGHT, S, WHITE
#Nothing changed exept making the hardcoded values scale based on settings scaling function and importing settings values

FONT_PATH = "TradeWinds-Regular.ttf"

_font_cache = {}
def tw(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(FONT_PATH, size)
    return _font_cache[size]


class CatchMode:
    WIN_DISPLAY_MS = 3500

    def __init__(self):
        self.active = False
        self.progress = 0
        self.won = False
        self.win_time = 0
        self.current_fish = None
        self.already_known = False
        self.runoff = False
        self.loss_time = 0

        self.add = 30
        self.sub = 15
        self.line_pos = pygame.Vector2(S(150), S(300))
        self.line_vel = pygame.Vector2(0, 0)
        self.damping = 0.97
        self.bounce_strength = 0.3
        self.scroll_sensitivity = 100

        self.green_pos = pygame.Vector2(0, S(300))
        self.green_vel = 0
        self.green_max_speed = 600
        self.green_accel = 900
        self.green_target = S(300.0)
        self.behavior_timer = 0
        self.bait_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

        self._runoff_sound_played = False

    def start(self, fish_info, start_y=None, already_known=False, bait_pos=None):
        self.active = True
        self.progress = 0
        self.won = False
        self.win_time = 0
        self.runoff = False
        self.already_known = already_known
        self.current_fish = fish_info
        self._runoff_sound_played = False
        _rand_start = random.uniform(S(top_bound2), S(bottom_bound2))
        self.line_pos.y = _rand_start
        self.line_vel.y = 0
        self.green_pos.y = _rand_start
        self.green_vel = 0
        self.green_target = _rand_start
        tier_settings = {
            "EASY":   (400, 400, 10,  10),
            "MEDIUM": (800, 600, 15, 15),
            "HARD":   (1200, 850, 25, 30),
        }
        ms, ac, add, sub = tier_settings.get(fish_info["difficulty"], (200, 300, 30, 15))
        self.green_max_speed = ms
        self.green_accel = ac
        self.add = add
        self.sub = sub
        self.tier = fish_info["difficulty"]
        self.speed = fish_info["speed"]

    def handle_scroll(self, scroll_amount):
        if not self.active or self.won:
            return
        self.line_vel.y -= scroll_amount * self.scroll_sensitivity * (1.0 + abs(scroll_amount) * 0.3)

    def update(self, dt, assets):
        if not self.active:
            return

        if self.won:
            if pygame.time.get_ticks() - self.win_time >= self.WIN_DISPLAY_MS:
                self.active = False
                self.won = False
            return

        if self.runoff:
            if pygame.time.get_ticks() - self.loss_time > 2000:
                self.active = False
                self.runoff = False
            return

        self.line_pos.y += self.line_vel.y * dt
        self.line_vel.y *= self.damping
        line_h = assets.line.get_height()
        half_h = line_h / 2

        if self.line_pos.y - half_h < S(top_bound2):
            self.line_pos.y = S(top_bound2) + half_h
            self.line_vel.y = abs(self.line_vel.y) * self.bounce_strength
        elif self.line_pos.y + half_h > S(bottom_bound2):
            self.line_pos.y = S(bottom_bound2) - half_h
            self.line_vel.y = -abs(self.line_vel.y) * self.bounce_strength

        self.behavior_timer -= dt * 1000
        if self.behavior_timer <= 0:
            if random.choice(["far", "near"]) == "far":
                self.green_target = random.uniform(S(top_bound2), S(bottom_bound2))
            else:
                self.green_target = max(S(top_bound2), min(S(bottom_bound2), self.green_pos.y + random.uniform(-S(120), S(120))))
            self.behavior_timer = random.randint(600, 1200)

        speed_mult = 1.0 + (self.speed - 1) * 0.25
        direction = self.green_target - self.green_pos.y
        if abs(direction) > 2:
            sign = 1 if direction > 0 else -1
            self.green_vel += sign * self.green_accel * speed_mult * min(1.0, abs(direction) / S(80.0)) * dt
        self.green_vel *= 0.995
        cap = self.green_max_speed * speed_mult
        self.green_vel = max(-cap, min(cap, self.green_vel))
        self.green_pos.y += self.green_vel * dt

        green_h = assets.green.get_height()
        if self.green_pos.y < S(top_bound2):
            self.green_pos.y = S(top_bound2)
            self.green_vel *= -0.5
            self.green_target = random.uniform(S(top_bound2) + S(50), S(bottom_bound2))
        elif self.green_pos.y + green_h > S(bottom_bound2):
            self.green_pos.y = S(bottom_bound2) - green_h
            self.green_vel *= -0.5
            self.green_target = random.uniform(S(top_bound2), S(bottom_bound2) - S(50))

        green_rect = assets.green.get_rect(topleft=(S(50), self.green_pos.y))
        line_rect  = assets.line.get_rect(center=(S(50) + assets.red.get_width() // 2, self.line_pos.y))

        self.progress += (self.add if line_rect.colliderect(green_rect) else -self.sub) * dt
        self.progress = max(-30, min(100, self.progress))

        if self.progress >= 100 and not self.won:
            self.won = True
            self.win_time = pygame.time.get_ticks()
        elif self.progress <= -30 and not self.runoff:
            self._stop(assets)

    def _stop(self, assets=None):
        self.progress = 0
        self.won = False
        self.runoff = True
        self.loss_time = pygame.time.get_ticks()

        if assets and not self._runoff_sound_played:
            self._runoff_sound_played = True
            assets.play_fail()

    def _draw_fish_preview(self, screen, assets):
        if not self.current_fish or self.won or self.runoff:
            return
        t = max(0.0, self.progress / 100.0)
        alpha = int(t * 255)
        img_size = S(250)
        img = pygame.transform.scale(
            getattr(assets, self.current_fish["image_key"]), (img_size, img_size)
        )
        img = img.copy()
        img.set_alpha(alpha)
        red_right = S(50) + assets.red.get_width()
        red_center_y = (S(top_bound2) + S(bottom_bound2)) // 2
        rect = img.get_rect(midleft=(red_right + S(20), red_center_y))
        screen.blit(img, rect)

    def draw(self, screen, assets):
        if not self.active:
            return

        name_font = tw(S(45))
        txt_font  = tw(S(40))
        size_font = tw(S(32))

        if not self.won and not self.runoff:
            self._draw_fish_preview(screen, assets)
            screen.blit(assets.red, (S(50), S(top_bound2)))
            self.green_pos.x = S(50) + assets.red.get_width() // 2 - assets.green.get_width() // 2
            screen.blit(assets.green, (self.green_pos.x, self.green_pos.y))
            screen.blit(assets.line, assets.line.get_rect(center=(S(50) + assets.red.get_width() // 2, self.line_pos.y)))

        if self.runoff:
            txt = txt_font.render("It escaped!", True, WHITE)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - S(350))))

        if self.won:
            fish = self.current_fish
            size = fish["size"]
            size_label = "Small" if size < 1.0 else "Normal" if size < 1.10 else "Big" if size < 1.25 else "Enormous"

            if self.already_known:
                top_gui_w, top_gui_h = S(900), S(110)
                top_gui_x = (WIDTH - top_gui_w) // 2
                top_gui_y = S(20)
                screen.blit(pygame.transform.scale(assets.gui, (top_gui_w, top_gui_h)), (top_gui_x, top_gui_y))
                msg = txt_font.render(f"You caught a {size_label} {fish['name']}!", True, WHITE)
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, top_gui_y + top_gui_h // 2)))
            else:
                img_size, padding, gap = S(350), S(50), S(50)
                caught_surf = name_font.render("You caught:", True, WHITE)
                name_surf2  = name_font.render(f"{fish['name']}!", True, WHITE)
                size_surf   = size_font.render(f"Size: {size_label}", True, (180, 220, 255))

                text_w = max(caught_surf.get_width(), name_surf2.get_width(), size_surf.get_width())
                text_h = caught_surf.get_height() + name_surf2.get_height() + size_surf.get_height() + S(16)
                panel_w = padding + img_size + gap + text_w + padding
                panel_h = max(img_size, text_h) + padding * 2
                panel_x = (WIDTH  - panel_w) // 2
                panel_y = (HEIGHT - panel_h) // 2

                screen.blit(pygame.transform.scale(assets.gui, (panel_w, panel_h)), (panel_x, panel_y))

                fish_img = pygame.transform.scale(getattr(assets, fish["image_key"]), (img_size, img_size))
                img_rect = fish_img.get_rect(midleft=(panel_x + padding, panel_y + panel_h // 2))
                screen.blit(fish_img, img_rect)

                text_x   = img_rect.right + gap
                center_y = panel_y + panel_h // 2
                lh = S(8)

                screen.blit(caught_surf, caught_surf.get_rect(midleft=(text_x, center_y - name_surf2.get_height() // 2 - caught_surf.get_height() - lh)))
                screen.blit(name_surf2,  name_surf2.get_rect(midleft=(text_x, center_y - name_surf2.get_height() // 2)))
                screen.blit(size_surf,   size_surf.get_rect(midleft=(text_x, center_y + name_surf2.get_height() // 2 + lh)))