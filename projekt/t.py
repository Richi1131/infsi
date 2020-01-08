import miniworldmaker as mwm
import time
import pygame
import matplotlib.image as image
import os
import math
import random


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/background.png")
        self.load_menu()
        self._last_time = None

    def act(self):
        global d_time
        current_time = time.time()
        if self._last_time is None:
            d_time = 0
        else:
            d_time = current_time - self._last_time

        self._last_time = time.time()

    def on_key_pressed(self, key):
        if "SPACE" in key and self.in_menu == True:
            self.set_level(0)

    def load_menu(self):
        self.clear()
        self.in_menu = True
        mwm.TextToken(position=(650, 300), font_size=50, color=(0, 0, 0, 255), text="Platzhalter")
        mwm.TextToken(position=(650, 800), font_size=20, color=(0, 0, 0, 255), text="Press SPACEBAR to start")

    def load_room(self):
        self.clear()
        self.in_menu = False
        self.load_gui()
        self.enemy_count = 0
        for object in self.room.content:
            for pos in object.positions:
                if object.type == Player:
                    self.player = Player(pos)
                else:
                    object.type(pos)
                    if object.type == Enemy:
                        self.enemy_count += 1

    def clear(self):
        for token in self.get_tokens_at_rect((pygame.Rect(0, 0, res[0], res[1]))):
            token.remove()
        
    def load_gui(self):
        global coins, bombs
        self.gui_coins = mwm.NumberToken(position=(725, 0), font_size=20, color=(0, 0, 0, 255), number=coins)
        self.gui_bombs = mwm.NumberToken(position=(775, 0), font_size=20, color=(0, 0, 0, 255), number=bombs)
        self.gui_health = mwm.NumberToken(position=(825, 0), font_size=20, color=(0, 0, 0, 255), number=100)
        
    def _set_room(self, room):
        self.room = room
        self.load_room()

    def _sync_room_to_level(self):
        try:
            if self.level != 0 and self.level % 10 == 0:
                self._set_room(boss_rooms[self.level//10])
            else:
                self._set_room(rooms[self.level-self.level//10])
        except IndexError:
            self.win()

    def set_level(self, level):
        self.level = level
        self._sync_room_to_level()

    def inc_level(self):
        self.level += 1
        self._sync_room_to_level()

    def win(self):
        self.clear()
        self.in_menu = True
        mwm.TextToken(position=(650, 400), font_size=50, color=(0, 0, 0, 255), text="You Win!")

    def loose(self):
        self.clear()
        self.in_menu = True
        mwm.TextToken(position=(650, 400), font_size=50, color=(0, 0, 0, 255), text="You Loose!")


class Room:
    def __init__(self, content=None):
        if content is None:
            self.content = list()
        else:
            self.content = content

    def add_object(self, object_class, positions: list):
        for item in self.content:
            if item.type == object_class:
                for pos in positions:
                    item.positions.append(pos)
                break
        else:
            self.content.append(RoomObject(object_class, positions))


class RoomObject:
    def __init__(self, type, positions: list):
        self.type = type
        self.positions = positions


class Player(mwm.Actor):
    def on_setup(self):
        self.add_image("images/char.png")
        self.speed = 5    # character move speed
        self.hp = 100    # character hit points
        self.shot_speed = 10    # bullet move speed
        self.shot_cool = .5    # time between shots
        self.damage = 50    # character damage per shot
        self.shot_buffer = 0    # time till next shot (on setup always 0)
        self.damage_buffer = 0    # time till able to take damage (on setup always 0)
        self.size = (80, 80)

    def on_key_pressed(self, key):
        # movement
        if "a" in key:
            if "w" in key:
                self.direction = -45
                self.move()
            elif "s" in key:
                self.direction = -135
                self.move()
            else:
                self.direction = -90
                self.move()
        elif "d" in key:
            if "w" in key:
                self.direction = 45
                self.move()
            elif "s" in key:
                self.direction = 135
                self.move()
            else:
                self.direction = 90
                self.move()
        elif "w" in key:
            self.direction = 0
            self.move()
        elif "s" in key:
            self.direction = 180
            self.move()
        # shooting
        if "left" in key:
            #self.costume.orientation = -self.direction - 90
            self.shoot(-90)
        elif "right" in key:
            #self.costume.orientation = -self.direction + 90
            self.shoot(90)
        elif "up" in key:
            #self.costume.orientation = -self.direction
            self.shoot(0)
        elif "down" in key:
            #self.costume.orientation = -self.direction + 180
            self.shoot(180)
        else:
            self.costume.orientation = 0

    def on_key_down(self, key):
        if "e" in key:
            global bombs
            if bombs > 0:
                BombExploding((self.position[0]-60, self.position[1]-60))
                bombs -= 1
                my_board.gui_bombs.set_number(bombs)

    def act(self):
        # collision (walls and borders)
        if self.sensing_token(Wall, 1) or self.sensing_borders() != []:
            self.move_back()
        # taking damage from enemies
        if self.sensing_token(Enemy, 1):
            self.on_hit(self.sensing_token(Enemy, 1).damage)
        # collecting coins
        if self.sensing_token(Coin, 1):
            self.sensing_token(Coin, 1).remove()
            global coins
            coins += 1
            my_board.gui_coins.inc()
        if self.sensing_token(BombItem, 1):
            self.sensing_token(BombItem, 1).remove()
            global bombs
            bombs += 1
            my_board.gui_bombs.inc()
        # leaving the room
        if self.sensing_token(Exit, 1):
            my_board.inc_level()

        if self.shot_buffer > 0:
            self.shot_buffer -= d_time
        if self.damage_buffer > 0:
            self.damage_buffer -= d_time

    def on_sensing_wall(self, wall):
        # additional collision to make glitches less common (not perfect)
        self.move_back()

    def on_hit(self, damage):
        if self.damage_buffer <= 0:
            self.hp -= damage
            self.damage_buffer = 1
            my_board.gui_health.set_number(self.hp)
            if self.hp <= 0:
                my_board.loose()
                return

    def on_blast(self):
        my_board.loose()

    def shoot(self, direction):
        if self.shot_buffer <= 0:
            Bullet(self, direction)
            self.shot_buffer = self.shot_cool


class Bullet(mwm.Token):
    def __init__(self, master, direction):
        self.master = master
        super().__init__(master.position)
        self.direction = direction
        self.speed = master.shot_speed
        self.damage = master.damage

    def on_setup(self):
        self.add_image("images/bullet.png")
        self.size = self.size = (10, 10)

    def act(self):
        self.move()
        if not self.sensing_on_board():
            self.remove()
            return
        if len(self.sensing_tokens()) > 1:
            for obj in self.sensing_tokens():
                if not isinstance(obj, Bullet) and not isinstance(obj, type(self.master)) and not isinstance(obj, Coin):
                    try:                                                   # ^ if bullet hits
                        obj.on_hit(self.damage)                            # -> trying to call on_hit() for target(s)
                    except AttributeError:
                        pass
                    self.remove()                                          # -> -> removing bullet
                    return
            return


class Wall(mwm.Token):
    def __init__(self, pos):
        super().__init__(pos)
        self.size = (tile_size[0], tile_size[1])

    def on_setup(self):
        self.add_image("images/wall.png")

    def on_blast(self):
        self.remove()


class DestructibleWall(Wall):
    def on_setup(self):
        self.add_image("images/destructible_wall.png")

    def on_hit(self, damage):
        self.remove()
        

class ExitLocation(mwm.Token):
    def on_setup(self):
        self.size = (tile_size[0], tile_size[1])
        self.add_image("images/empty.png")

    def act(self):
        if my_board.enemy_count == 0:
            Exit((self.position[0]-50, self.position[1]-50))
            self.remove()
            

class Exit(mwm.Token):
    def on_setup(self):
        self.size = (tile_size[0], tile_size[1])
        self.add_image("images/exit.png")
        if self.position[1] <= 50:
            self.direction = 180
        elif self.position[0] <= 50:
            self.direction = 90
        elif self.position[0] >= 1550:
            self.direction = -90
        

class Coin(mwm.Token):
    def on_setup(self):
        self.add_image("images/coin.png")
        self.size = (80, 80)
        self.position = (self.position[0]+10, self.position[1]+10)


class BombItem(mwm.Token):
    def on_setup(self):
        self.add_image("images/bomb_item.png")
        self.size = (100, 100)


class BombExploding(mwm.Token):
    def on_setup(self):
        self.add_image("images/bomb_exploding.png")
        self.size = (100, 100)
        self.explosion_buffer = 1.2

    def act(self):
        if self.explosion_buffer < 0:
            Explosion((self.position[0]-150, self.position[1]-150))
            self.remove()
            return
        else:
            self.explosion_buffer -= d_time


class Explosion(mwm.Token):
    def on_setup(self):
        self.add_image("images/explosion.png")
        self.size = (300, 300)
        self.remove_buffer = 0.15

    def act(self):
        if self.remove_buffer < 0:
            self.remove()
            return
        for token in self.sensing_tokens():
            try:
                token.on_blast()
            except AttributeError:
                pass
        self.remove_buffer -= d_time

class Enemy(mwm.Token):
    def on_setup(self):
        self.add_image("images/enemy.png")
        self.size = (80, 80)
        self.hp = 100
        self.damage = 50
        self.speed = 4
        self.target_position = None
        self.move_buffer = 0

    def act(self):
        if self.sensing_token(Wall, 1) or self.sensing_borders() != []:
            self.move_back()
        self.target_position = my_board.player.position
        self.move_to_target()

    def move_to_target(self):
        if self.target_position is not None:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            if abs(round(dx, -1)) == abs(round(dy, -1)):
                if dx > 0 and dy > 0:
                    self.direction = 135
                elif dx < 0 and dy < 0:
                    self.direction = -45
                elif dy < 0 < dx:
                    self.direction = 45
                elif dx < 0 < dy:
                    self.direction = -135
            elif abs(dx) < abs(dy):
                if dy < 0:
                    self.direction = 0
                else:
                    self.direction = 180
            else:
                if dx < 0:
                    self.direction = -90
                else:
                    self.direction = 90
            self.move()

    def on_hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.remove()
            my_board.enemy_count -= 1
            return

    def on_blast(self):
        self.remove()
        my_board.enemy_count -= 1
        

def read_levels():
    global rooms, boss_rooms
    rooms = list()
    path = "maps"
    build_levels(path, rooms)

    boss_rooms = list()
    path = "maps/boss"
    build_levels(path, boss_rooms)


def build_levels(path, save_location):
    folder = os.listdir(path)
    folder.sort()
    for file in folder:
        if file.endswith(".png"):
            save_location.append(Room())
            data = image.imread(f"{path}/{file}")
            for y, line in enumerate(data):
                for x, col in enumerate(line):
                    col = [round(x, 1) for x in list(col)]
                    try:
                        save_location[len(save_location)-1].add_object(drawables[str(col)], [(x * tile_size[0], y * tile_size[1])])
                    except KeyError:
                        pass


res = (1600, 900)
tile_count_x = 16
tile_count_y = 9
tile_size = (100, 100)

d_time = 0

drawables = {
    "[0.0, 0.0, 1.0, 1.0]": Player,                 # RGBA(0,0,255,255)
    "[0.0, 0.0, 0.0, 1.0]": Wall,                   # RGBA(0,0,0,255)
    "[0.0, 0.5, 0.0, 1.0]": DestructibleWall,       # RGBA(0,~127,0,255)
    "[1.0, 0.8, 0.0, 1.0]": Coin,                   # RGBA(255,~200,0,255)
    "[1.0, 0.0, 0.0, 1.0]": Enemy,                  # RGBA(255,0,0,255)
    "[0.5, 0.5, 0.0, 1.0]": ExitLocation,           # RGBA(~127,~127,0,255)
    "[0.5, 0.5, 0.5, 1.0]": BombItem                # RGBA(~127,~127,~127,255)
}

#savedata
coins = 0
bombs = 10

read_levels()
my_board = MyBoard(res[0], res[1])
my_board.show(fullscreen=True)
