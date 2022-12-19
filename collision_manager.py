import pygame
from objects import Explosion, Pow
import random


class CollisionManager:

    def __init__(self, player, game, spawn_manager, music_manager):
        self.player = player
        self.game = game
        self.spawn_manager = spawn_manager
        self.music_manager = music_manager
        self.death_explosion = None

    def player_mob(self):
        hits = pygame.sprite.spritecollide(self.player, self.game.mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            self.player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            self.game.all_sprites.add(expl)
            self.spawn_manager.newmob(self.game)
            if self.player.shield <= 0:
                self.death_explosion = Explosion(self.player.rect.center, 'player')
                self.game.all_sprites.add(self.death_explosion)
                self.player.hide()
                self.player.lives -= 1
                self.player.shield = self.player.maxshield
                self.music_manager.fart_sound.play()
            if self.player.lives == 0:
                self.player.alive = False
                self.player.shield = 0

    def player_pow(self):
        hits = pygame.sprite.spritecollide(self.player, self.game.powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                self.player.shield += random.randrange(10, 30)
                if self.player.shield >= self.player.maxshield:
                    self.player.shield = self.player.maxshield
                self.music_manager.shield_sound.play()
            if hit.type == 'gun':
                self.player.powerup()
                self.music_manager.power_sound.play()

    def mob_bullet(self):
        hits = pygame.sprite.groupcollide(self.game.mobs, self.game.bullets, False, True)
        for hit in hits:
            hit.lives -= 1
            if hit.lives > 0:
                random.choice(self.music_manager.expl_sounds).play()
                expl_center = (hit.rect.center[0], hit.rect.bottom)
                expl = Explosion(expl_center, 'sm')
                self.game.all_sprites.add(expl)
            else:
                hit.kill()
                self.game.score += 50 + hit.radius  # Очки считаются от радиуса
                random.choice(self.music_manager.expl_sounds).play()
                expl = Explosion(hit.rect.center, 'lg')
                self.game.all_sprites.add(expl)
                if random.random() > 0.9 + self.player.power / 170 - 0.01:
                    pov = Pow(hit.rect.center)
                    self.game.all_sprites.add(pov)
                    self.game.powerups.add(pov)
                self.spawn_manager.newmob(self.game)

    def boss_bullet(self):
        hits = pygame.sprite.groupcollide(self.game.boss, self.game.bullets, False, True, pygame.sprite.collide_circle)
        if hits:
            for hit in list(hits.values())[0]:
                hit_obj = [x for x in hits.keys()][0]

                hit_obj.lives -= 1
                if hit_obj.lives > 0:
                    random.choice(self.music_manager.expl_sounds).play()
                    expl_center = (hit.rect.center[0], hit.rect.center[1])
                    expl = Explosion(expl_center, 'sm')
                    self.game.all_sprites.add(expl)
                else:
                    hit.kill()
                    self.game.score += 5000 + hit.radius  # Очки считаются от радиуса
                    random.choice(self.music_manager.expl_sounds).play()
                    expl = Explosion(hit.rect.center, 'lg')
                    self.game.all_sprites.add(expl)
                    if random.random() > 0.9 + self.player.power / 170 - 0.01:
                        pov = Pow(hit.rect.center)
                        self.game.all_sprites.add(pov)
                        self.game.powerups.add(pov)
                    self.spawn_manager.newmob(self.game)
                hit.kill()

    def boss_mob(self):
        hits = pygame.sprite.groupcollide(self.game.boss, self.game.mobs, False, True, pygame.sprite.collide_circle)
        if hits:
            for hit in list(hits.values())[0]:
                hit_obj = [x for x in hits.keys()][0]

                hit_obj.lives -= 1
                if hit_obj.lives > 0:
                    random.choice(self.music_manager.expl_sounds).play()
                    expl_center = (hit.rect.center[0], hit.rect.center[1])
                    expl = Explosion(expl_center, 'sm')
                    self.game.all_sprites.add(expl)
                else:
                    hit.kill()
                    random.choice(self.music_manager.expl_sounds).play()
                    expl = Explosion(hit.rect.center, 'lg')
                    self.game.all_sprites.add(expl)
                hit.kill()

    def player_enemy_bullet(self):
        hits = pygame.sprite.spritecollide(self.player, self.game.enemy_bullets, True)
        for hit in hits:
            self.player.shield -= 50
            expl = Explosion(hit.rect.center, 'sm')
            self.game.all_sprites.add(expl)
            self.spawn_manager.newmob(self.game)
            if self.player.shield <= 0:
                self.death_explosion = Explosion(self.player.rect.center, 'player')
                self.game.all_sprites.add(self.death_explosion)
                self.player.hide()
                self.player.lives -= 1
                self.player.shield = self.player.maxshield
                self.music_manager.fart_sound.play()
            if self.player.lives == 0:
                self.player.alive = False

    def player_boss_bullet(self):
        hits = pygame.sprite.spritecollide(self.player, self.game.boss_bullets, True)
        for hit in hits:
            self.player.shield -= 10000
            expl = Explosion(hit.rect.center, 'sm')
            self.game.all_sprites.add(expl)
            if self.player.shield <= 0:
                self.death_explosion = Explosion(self.player.rect.center, 'player')
                self.game.all_sprites.add(self.death_explosion)
                self.player.hide()
                self.player.lives -= 1
                self.player.shield = self.player.maxshield
                self.music_manager.fart_sound.play()
            if self.player.lives == 0:
                self.player.alive = False

    def bullet_enemy(self):
        hits = pygame.sprite.groupcollide(self.game.enemies, self.game.bullets, False, True)
        for hit in hits:
            hit.lives -= 1
            if hit.lives > 0:
                random.choice(self.music_manager.expl_sounds).play()
                expl_center = (hit.rect.center[0], hit.rect.bottom)
                expl = Explosion(expl_center, 'sm')
                self.game.all_sprites.add(expl)
            else:
                hit.kill()
                self.game.score += 500
                random.choice(self.music_manager.expl_sounds).play()
                expl = Explosion(hit.rect.center, 'lg')
                self.game.all_sprites.add(expl)
                if random.random() > 0.9 + self.player.power / 170 - 0.01:
                    pov = Pow(hit.rect.center)
                    self.game.all_sprites.add(pov)
                    self.game.powerups.add(pov)

    def boss_player(self):
        hits = pygame.sprite.spritecollide(self.player, self.game.boss, False)
        for hit in hits:
            self.player.shield -= 10000
            expl = Explosion(hit.rect.center, 'sm')
            self.game.all_sprites.add(expl)
            if self.player.shield <= 0:
                self.death_explosion = Explosion(self.player.rect.center, 'player')
                self.game.all_sprites.add(self.death_explosion)
                self.player.hide()
                self.player.lives -= 1
                self.player.shield = self.player.maxshield
                self.music_manager.fart_sound.play()
            if self.player.lives == 0:
                self.player.alive = False

    def process_all_collisions(self):
        self.player_mob()
        self.player_pow()
        self.mob_bullet()
        self.boss_bullet()
        self.boss_mob()
        self.player_enemy_bullet()
        self.player_boss_bullet()
        self.bullet_enemy()
        self.boss_player()
