import pygame
from settings import HEIGHT, S, top_bound, bottom_bound
from scaling import Scale


"""FISHING CLASS RESPONSIBLE FOR ROD AND BAIT MOVEMENT AND IMAGES"""

COLOR_MAP = {"default": "n", "black": "b", "pink": "p"} #Map rod color variants matching the shop 


class FishingSystem:
    def __init__(self, shop, game):
        #Fishing system will get called with 2 parameters: game and shop (Game and Shop class), calling it this way makes sure that there wont be double imported
        self.shop = shop
        self.game = game
        self.assets = game.assets #Use assets , take the dependency from Game class 

        self.tier_top_bounds = {1: 533, 2: 333, 3: 100} #Adding tier bounds as arrays so it can be eaisly used later

        #Making a vector offset from rod images (since the rod right and rod half right are flipped versions of left and half left the without this the rod would be uneven on the screen.
        self.rod_handle_offsets = [ 
            pygame.Vector2(130, 370),
            pygame.Vector2(129, 371),
            pygame.Vector2(129, 371),
            pygame.Vector2(171, 371),
            pygame.Vector2(170, 370),
        ]
        #The same but just with rod tops, used in Rope() class to calculate starting rope point 
        self.rod_top_offsets = [
            pygame.Vector2(127, 366),
            pygame.Vector2(81,  (371),
            pygame.Vector2(0,       -371),
            pygame.Vector2(81,   -371),
            pygame.Vector2(127,  -366),
        ]

        self.rod_pos = pygame.Vector2(960, HEIGHT) #Starting rod position, althought it wont change mich later.
        self._zone_index = 2 #Calculating current zone (0-4) used to decide what rod image would be used; Start with zone 2 (middle)
        self.rod_top = self.rod_pos + self.rod_top_offsets[2] #Calculating rod top from ealier offset and positon

        self.bait_pos = pygame.Vector2(960, HEIGHT // 2) #Starting bait positon, higher than rod but on the same x-axis
        self.bait_vel = pygame.Vector2(0, 0) #Empty Bait velocity vector , used for later calcualtions
        #Hardcoded physics values
        self.spring  = 0.1
        self.damping = 0.3
        self.speed   = 0.0

        self.bait_img = self._get_bait_img() #Using _get_bait to get current bait image (line 60)
        self.scaler = Scale(self.bait_img) #Scaling bait image using the Scale class
        self._build_rod_states() #Calling function (line 56)
        self.rod_img = self.rod_states[2] # based on rod state (0-4) call the corresponding image

    def _color_key(self):  #Getting the rod variant from shop, setting the defalut one to be well.. normal
        return COLOR_MAP.get(self.shop.rod_cosmetic.get(self.shop.rod_tier, "default"), "n") 

    def _build_rod_states(self): #Based on tier and colour key get the 5 state images for current rod
        tier, ck = self.shop.rod_tier, self._color_key()
        self.rod_states = [self.assets.get_rod(tier, ck, o) for o in ("l", "hl", "f", "hr", "r")]

    def _get_bait_img(self): #3rd tier of rod has custom bait based on colour, write if function calling the bait image if tier is 3 and use the currrent colour_key.
        tier = self.shop.rod_tier
        if tier == 1:
            return self.assets.bait_1
        if tier == 2:
            return self.assets.bait_2
        color = self.shop.rod_cosmetic.get(3, "default")
        return {"default": self.assets.bait_3_n, "black": self.assets.bait_3_b, "pink": self.assets.bait_3_p}.get(color, self.assets.bait_3_n) 

    def get_top_bound(self): #Get the current rod tier and based on it check the top_bound, by defalut make it the smallest one.
        return self.tier_top_bounds.get(self.shop.rod_tier, 533)

    def get_depth(self):
        return max(0.0, min(1.0, (S(bottom_bound) - self.bait_pos.y) / (S(bottom_bound) - S(top_bound))))

    def update(self):
        self._build_rod_states()
        new_bait = self._get_bait_img()
        if new_bait is not self.bait_img:
            self.bait_img = new_bait
            self.scaler = Scale(self.bait_img)

        current_top = self.get_top_bound()
        mx, my = pygame.mouse.get_pos()
        target = pygame.Vector2(mx, max(current_top, min(S(bottom_bound), my)))

        self.bait_vel += (target - self.bait_pos) * self.spring
        self.bait_vel *= self.damping
        self.bait_pos += self.bait_vel
        self.bait_pos.y = max(current_top, min(S(bottom_bound), self.bait_pos.y))

        self._zone_index = max(0, min(4, int(self.bait_pos.x // S(384))))
        self.rod_img = self.rod_states[self._zone_index]
        self.rod_pos.x = S(960)
        self.rod_pos.y = HEIGHT
        self.rod_top = self.rod_pos + self.rod_top_offsets[self._zone_index]
        self.speed = self.bait_vel.length()

    def draw(self, screen):
        scale = 0.5 + 0.5 * ((self.bait_pos.y - S(top_bound)) / (S(bottom_bound) - S(top_bound))) * 2
        scaled_bait = self.scaler.get_scaled(scale)
        screen.blit(self.rod_img, self.rod_pos - self.rod_handle_offsets[self._zone_index])
        screen.blit(scaled_bait, scaled_bait.get_rect(center=self.bait_pos))

