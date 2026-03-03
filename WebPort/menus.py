import pygame
import sys
from settings import *

FONT_PATH = "TradeWinds-Regular.ttf"
#Got rid of mouse sensitivy and windowed mode settings since they dont work
#Got rid of leave button on main menu since that doesnt really work on web


class Menus:
    def __init__(self, game):
        self.game               = game
        self.screen             = self.game.screen
        self.font               = game.font
        self.clock              = game.clock
        self.ui                 = game.ui
        self.in_game_menu_open  = False

    def _btn(self, w, h):
        return pygame.transform.scale(self.game.assets.button_img, (w, h))

    def _btnh(self, w, h):
        return pygame.transform.scale(self.game.assets.button_hover_img, (w, h))

    def draw_main_menu(self):
        pygame.mouse.set_visible(True)
        bw, bh = S(560), S(110)
        btn, btnh = self._btn(bw, bh), self._btnh(bw, bh)

        if self.ui.button(btn, btnh, S(110), S(620), "New Game"):
            self.game.new_game()

        if self.game.save_system.has_save():
            if self.ui.button(btn, btnh, S(110), S(750), "Continue"):
                if self.game.save_system.load(self.game):
                    self.game.state = "game"
        else:
            grey = self._btn(bw, bh).copy()
            grey.set_alpha(100)
            self.screen.blit(grey, (S(110), S(750)))
            cant = pygame.font.Font(FONT_PATH, S(35)).render("Continue", True, (120, 120, 120))
            self.screen.blit(cant, cant.get_rect(center=(S(110) + bw // 2, S(750) + bh // 2)))

        if self.ui.button(btn, btnh, S(110), S(880), "Options"):
            self.game.state = "options"


    def _draw_options_bg(self, dt_ms):
        surf = self.game.assets.get_gif_frame("options_bg", self.game.assets.options_bg_frames, dt_ms)
        self.screen.blit(surf, (0, 0))

    def _draw_volume(self, cx, vol_y, sens_y): #Got rid of mouse sensitivity slider, made it text
        self.game.music_volume = self.ui.slider(
            "Music Volume", cx - S(200), vol_y, S(400),
            self.game.music_volume, 0.0, 1.0,
            assets=self.game.assets, show_value=True
        )
        note_font = pygame.font.Font(FONT_PATH, S(20))
        bw, bh = S(560), S(110)
        btnh = self._btnh(bw, bh)
        self.screen.blit(btnh, btnh.get_rect(centerx=cx, top=sens_y - S(45)))
        note_surf = note_font.render("Mouse sensitivity only aviabe on desktop", True, (254, 254, 254))
        self.screen.blit(note_surf, note_surf.get_rect(centerx=cx, top=sens_y))

    def draw_options(self, dt_ms=0): #Made the fulscreen button be text
        self._draw_options_bg(dt_ms)
        cx     = WIDTH // 2
        bw, bh = S(560), S(110)
        btn_x  = cx - bw // 2
        btn, btnh = self._btn(bw, bh), self._btnh(bw, bh)

        note_font = pygame.font.Font(FONT_PATH, S(24))
        note_surf = note_font.render("Windowed mode only aviabe on desktop", True, (254, 254, 254))
        self.screen.blit(btnh, btnh.get_rect(topleft=(btn_x, S(145))))
        self.screen.blit(note_surf, note_surf.get_rect(topleft=(cx - S(220), S(180))))

        self._draw_volume(cx, S(410), S(590))

        if self.ui.button(btn, btnh, btn_x, S(730), "Credits"):
            self.game.state = "credits"
        if self.ui.button(btn, btnh, btn_x, S(860), "Back"):
            self.game.state = "menu"

    def draw_credits(self, dt_ms=0):
        self._draw_options_bg(dt_ms)
        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(120)
        dark.fill((0, 0, 0))
        self.screen.blit(dark, (0, 0))

        small_font = pygame.font.Font(FONT_PATH, S(18))

        credits_data = [
            (self.font,  "Created by: Sue"),
            (self.font,  "Graphics: Sue"),
            (small_font, " "),
            (self.font,  "Music From FreeSound.org:"),
            (small_font, "FunWithSound: Success Fanfare Trumpets.mp3"),
            (small_font, "sweet_niche: Trumpet_Cry.wav"),
            (small_font, "richwise: Waterside, foggy morning"),
            (small_font, "Jay_You: music elevator ext part 1/3"),
            (small_font, "paulprit: Angel Fly Fish Reel Slow Pull_1.wav"),
            (small_font, "Robinhood76: 05966 water surfacing splashes.wav"),
            (small_font, "Duisterwho: Awesome man - vocal"),
            (small_font, "AlienXXX: Tearing_rotten_wood_5a.wav"),
            (small_font, "NachtmahrTV: Shop Bell"),
            (small_font, "IENBA: Page Turn"),
            (small_font, "Omiranda14: SFX_Spell_IceShoot_02"),
            (small_font, " "),
            (self.font,  "Thanks for playing <3!"),
        ]

        y = S(80)
        for font, line in credits_data:
            surf = font.render(line, True, WHITE)
            self.screen.blit(surf, (S(100), y))
            y += font.get_height() + S(10)

        bw, bh = S(560), S(110)
        if self.ui.button(self._btn(bw, bh), self._btnh(bw, bh), S(150), HEIGHT - S(200), "Back"):
            self.game.state = "options"
        pygame.display.flip()

    def draw_inoptions(self, dt_ms=0):
        self._draw_options_bg(dt_ms)
        cx     = WIDTH // 2
        bw, bh = S(560), S(110)
        btn_x  = cx - bw // 2

        self._draw_volume(cx, S(390), S(570))

        if self.ui.button(self._btn(bw, bh), self._btnh(bw, bh), btn_x, S(720), "Back"):
            self.game.state        = "in_menu"
            self.in_game_menu_open = True
        pygame.display.flip()

    def draw_in_game_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        bw, bh  = S(560), S(110)
        btn, btnh = self._btn(bw, bh), self._btnh(bw, bh)
        menu_x  = int(WIDTH * 0.355)
        start_y = int(HEIGHT * 0.355)
        gap     = S(20)

        if self.ui.button(btn, btnh, menu_x, start_y, "Continue"):
            self.in_game_menu_open = False
            self.game.state        = "game"

        if self.ui.button(btn, btnh, menu_x, start_y + bh + gap, "Options"):
            self.game.state        = "options2"
            self.in_game_menu_open = False

        if self.ui.button(btn, btnh, menu_x, start_y + 2 * (bh + gap), "Quit to Menu"):
            self.game.assets.stop_reel()
            self.game.splashes.clear(self.game.assets)
            self.game.save_system.save(self.game)
            self.game.state        = "menu"
            self.in_game_menu_open = False

