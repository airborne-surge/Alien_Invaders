import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """A class to manage bullets fired from the ship"""

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position"""
        # initiate the superclass (Sprite)
        super().__init__()
        # bullet's screen is same as games
        self.screen = ai_game.screen
        # gather settings from game
        self.settings = ai_game.settings
        # get bullet color from settings
        self.color = self.settings.bullet_color

        # create a bullet rect at (0,0) and then set the correct position (manually creating rect)
        self.rect = pygame.Rect(0,0,self.settings.bullet_width,self.settings.bullet_height)
        # set the bullet to fire from the middle of the ship
        self.rect.midtop = ai_game.ship.rect.midtop

        # store the bullet's position as a decimal value
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen"""
        # update the decimal position on the bullet
        self.y -= self.settings.bullet_speed
        # update the rect position
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen"""
        pygame.draw.rect(self.screen,self.color,self.rect)