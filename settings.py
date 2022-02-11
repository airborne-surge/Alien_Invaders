import pygame

class Settings:
    """Class stores settings for Alien Invasion game."""

    def __init__(self):
        """Initialize the game settings"""
        # screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        # # choose image to use as background
        # self.background = 'images/space.bmp'

        # ship settings
        self.ship_speed = 1.5
        # self.ship_limit = 3
        # TODO for testing
        self.ship_limit = 1

        # bullet settings
        self.bullet_speed = 1.0
        # self.bullet_width = 3
        # TODO for testing
        self.bullet_width = 3000
        self.bullet_height = 15
        self.bullet_color = (80,100,0)
        self.bullets_allowed = 3

        # alien settings
        self.alien_speed = 1.0
        # self.fleet_drop_speed = 10
        # TODO for testing
        self.fleet_drop_speed = 100
        # fleet direction of 1 represents right; -1 represents left
        self.fleet_direction = 1

        # how quickly the game speeds up
        self.speedup_scale = 1.1

        # alien point value multiplier
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game"""
        self.ship_speed = 2.0
        self.bullet_speed = 4.0
        self.alien_speed = 0.2

        # fleet direction of 1 represents right; -1 represents left
        self.fleet_direction = 1

        # scoring
        self.alien_points = 20

    # TODO make changes to bullet size and location if possible here
    def increase_speed(self):
        """Increase speed settings and alien point values"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
