import pygame
import random
import math
import fish_data
from settings import WIDTH, HEIGHT, S, bottom_bound, WHITE
#Nothing changed exept making the hardcoded values scale based on settings scaling function and importing settings values


GLOBAL_TOP = S(100)

DIFFICULTY_CONFIG = {
    "EASY":   {"spawn_top": S(566), "duration": 5000, "scare_speed": 20, "scare_dist": S(50),  "size_range": (0.75, 1.25)},
    "MEDIUM": {"spawn_top": S(333), "duration": 4000, "scare_speed": 13, "scare_dist": S(75),  "size_range": (0.75, 1.25)},
    "HARD":   {"spawn_top": S(100), "duration": 3000, "scare_speed": 8,  "scare_dist": S(100), "size_range": (0.75, 1.25)},
}


class Splashing:
    def __init__(self, fishing_instance, shop):
        self.splashes = []
        self.fishing = fishing_instance
        self.shop = shop
        self.scare_message = ""
        self.scare_timer = 0

    def spawn(self, current_time, assets):
        if self.splashes:
            return

        difficulty = random.choice(self.shop.get_allowed_tiers())
        config = DIFFICULTY_CONFIG[difficulty]

        available = [n for n, info in fish_data.FISH_DATA.items() if info.get("tier") == difficulty]
        if not available:
            return

        name = random.choice(available)
        info = fish_data.FISH_DATA[name]

        zone_top    = {"EASY": S(566), "MEDIUM": S(333), "HARD": S(100)}[difficulty]
        zone_bottom = {"EASY": S(bottom_bound), "MEDIUM": S(566), "HARD": S(333)}[difficulty]
        temp_y = int(random.uniform(zone_top, zone_bottom))

        scale_factor = 0.5 + 0.5 * ((temp_y - GLOBAL_TOP) / (S(bottom_bound) - GLOBAL_TOP)) * 0.75
        size_mult = random.uniform(*config["size_range"])

        frame_surf, _ = assets.splash_frames[0]
        base_w = int(frame_surf.get_width()  * scale_factor)
        base_h = int(frame_surf.get_height() * scale_factor)

        x_pos = random.randint(0, max(0, WIDTH - base_w))
        y_pos = max(zone_top, min(zone_bottom - base_h, temp_y))

        self.splashes.append({
            "rect":       pygame.Rect(x_pos, y_pos, base_w, base_h),
            "spawn_time": current_time,
            "duration":   config["duration"],
            "difficulty": difficulty,
            "fish_info": {
                "name":       name.replace("_", " "),
                "difficulty": difficulty,
                "size":       round(size_mult, 2),
                "price":      int(info["price"] * size_mult),
                "speed":      info["speed"],
                "image_key":  info["image_key"],
            },
        })

        assets.play_splash()

    def update(self, assets=None):
        current = pygame.time.get_ticks()
        surviving = []
        for s in self.splashes:
            if current - s["spawn_time"] > s["duration"]:
                if assets:
                    assets.stop_splash()
                continue
            config = DIFFICULTY_CONFIG[s["difficulty"]]
            dist = math.hypot(
                self.fishing.bait_pos.x - s["rect"].centerx,
                self.fishing.bait_pos.y - s["rect"].centery,
            )
            if dist < config["scare_dist"] and self.fishing.speed > config["scare_speed"]:
                self.scare_message = "The Fish was scared off!"
                self.scare_timer = current
                if assets:
                    assets.stop_splash()
                    assets.play_fail()
                continue
            surviving.append(s)
        self.splashes = surviving

    def clear(self, assets=None):
        self.splashes = []
        if assets:
            assets.stop_splash()

    def draw(self, screen, assets, font, dt_ms=0):
        current_time = pygame.time.get_ticks()
        for splash in self.splashes:
            elapsed = current_time - splash["spawn_time"]
            surf = assets.get_splash_frame_at(elapsed, splash["duration"], assets.splash_frames)
            screen.blit(
                pygame.transform.scale(surf, (splash["rect"].width, splash["rect"].height)),
                splash["rect"],
            )

        if current_time - self.scare_timer < 2000:
            txt = font.render(self.scare_message, True, WHITE)
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, S(150))))

    def get_clicked_splash(self, mouse_pos, assets=None):
        for splash in self.splashes:
            if splash["rect"].collidepoint(mouse_pos):
                self.splashes.remove(splash)
                if assets:
                    assets.stop_splash()
                return splash["fish_info"]
        return None