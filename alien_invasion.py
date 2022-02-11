import sys
import random
import time
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard


class AlienInvasion:
    """ Manages game assets and game behavior."""

    def __init__(self):
        """Initialize the game and create game resources"""
        pygame.init()
        self.settings = Settings(self)

        # screen settings for 1200x800
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        # TODO
        # use image for background
        self.background = pygame.image.load(self.settings.background)
        # scale the image to the game window
        self.background = pygame.transform.scale(self.background,
                                                 (self.settings.screen_width, self.settings.screen_height))

        # # screen settings for full screen TODO may be able to map button to activate full screen
        # self.screen = pygame.display.set_mode( (0, 0), pygame.FULLSCREEN )
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height

        # window title
        pygame.display.set_caption("Alien Invasion")

        # create instance to store game statistics
        self.stats = GameStats(self)

        # create a gameboard
        self.sb = ScoreBoard(self)

        # create the ship.
        self.ship = Ship(self)

        # create sprite grouping for bullets
        self.bullets = pygame.sprite.Group()

        # group to hold aliens
        self.aliens = pygame.sprite.Group()

        # make the fleet of aliens
        self._create_fleet()

        # make the play button
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Runs game by starting main loop."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _check_events(self):
        """Respond to key-presses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # key pressed
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            # key unpressed
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            # TODO add elif to start game by pressing enter

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        # button area only active when game is inactive. prevents accidental restarts.
        if button_clicked and not self.stats.game_active:
            # reset the game settings
            self.settings.initialize_dynamic_settings()

            # reset the game statistics
            self.stats.reset_stats()
            self.stats.game_active = True

            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # clear screen of aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # hide the mouse cursor
            pygame.mouse.set_visible(False)

    def _update_bullets(self):
        """Update the position of bullets and get rid of old bullets"""

        # update bullet positions
        self.bullets.update()

        # get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets))

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions"""
        # check for any bullets that have hit aliens. get rid of bullet and alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        # increment points for shooting down alien ship
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        # check if entire fleet of aliens destroyed after last barrage of bullets
        if not self.aliens:
            # destroy existing bullets
            self.bullets.empty()

            # increase level
            self.stats.level += 1

            # TODO change background image
            background_index = (self.stats.level - 1) % len(self.settings.level_backgrounds)
            self.background = pygame.image.load(self.settings.level_backgrounds[background_index])
            # scale the image to the game window
            self.background = pygame.transform.scale(self.background,
                                                     (self.settings.screen_width, self.settings.screen_height))

            # create new fleet
            self._create_fleet()
            self.settings.increase_speed()

            # display new level
            self.sb.prep_level()

    def _update_aliens(self):
        """ Check if the fleet is at an edge, then update position of all aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        # look for alien ship collisions TODO closest alien row to ship is colliding about one row above ship
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create fleet of aliens"""
        # alien used for calculating position of fleet. will not be part of fleet.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        # subtract an alien's width from left margin and from right margin of screen
        available_space_x = self.settings.screen_width - (2 * alien_width)
        # partition this available space to determine number of aliens that will fit with one alien_width buffer space
        # on left and right of each alien
        number_aliens_x = available_space_x // (2 * alien_width)

        # determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        # two alien_heights from the top of the screen + (one ship_height + one alien_height from bottom of screen)
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        # one alien_height buffer on top of alien and one on bottom
        number_rows = available_space_y // (2 * alien_height)
        # create the fleet
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row"""

        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        # if any ship lives left, reset screen and play again
        if self.stats.ships_left > 0:
            # decrement ships left, and update count of ships left on screen
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # treat the same as if ship got hit
                self._ship_hit()
                break

    def _update_screen(self):
        """Update images on the screen and flip to the new screen"""
        # self.screen.fill(self.settings.bg_color)
        # TODO
        # # draw background image
        self.screen.blit(self.background, (0, 0))
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # draw the score information
        self.sb.show_score()

        # draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _check_keydown_events(self, event):
        """Respond to key-presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        # TODO added self.stats.game_active to prevent bullet from firing after game over
        if (len(self.bullets) < self.settings.bullets_allowed) and self.stats.game_active:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


if __name__ == '__main__':
    # Make an instance of the game and run that instance
    ai = AlienInvasion()
    ai.run_game()
