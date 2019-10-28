import miniworldmaker as mwm
import time
import pygame
import matplotlib.image as image
import os
import random


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        Player((100, 100))
        Wall((0, 0))
        DestructibleWall((50, 0))
        Enemy((400, 400))
        self.set_room(rooms[0])

    def on_key_pressed(self, key):
        if "f11" in key:
            self.reset()

    def load_room(self):
        for token in self.get_tokens_at_rect((pygame.Rect(0, 0, res[0], res[1]))):
            token.remove()
        for object in self.room.content:
            for pos in object.positions:
                object.type(pos)

    def set_room(self, room):
        self.room = room
        self.load_room()


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

    def act(self):
        self.cool()   # processing passed time
        # collision (walls and borders)
        if self.sensing_token(Wall, 1) or self.sensing_borders() != []:
            self.move_back()
        # taking damage from enemies
        if self.sensing_token(Enemy, 1):
            self.on_hit(self.sensing_token(Enemy, 1).damage)
        # collection coins
        if self.sensing_token(Coin, 1):
            self.sensing_token(Coin, 1).remove()

    def on_sensing_wall(self, wall):
        # additional collision to make glitches less common (not perfect)
        self.move_back()

    def on_hit(self, damage):
        if self.damage_buffer <= 0:
            self.hp -= damage
            self.damage_buffer = 1
            if self.hp <= 0:
                self.remove()
                return

    def shoot(self, direction):
        if self.shot_buffer <= 0:
            Bullet(self, direction)
            self.shot_buffer = self.shot_cool

    def cool(self):
        global d_time
        time_2 = time.time()
        try:
            d_time = time_2 - self.time
        except AttributeError:
            d_time = 0

        if self.shot_buffer > 0:
            self.shot_buffer -= d_time
        if self.damage_buffer > 0:
            self.damage_buffer -= d_time

        self.time = time.time()


class Bullet(mwm.Token):
    def __init__(self, master, direction):
        self.master = master
        super().__init__((master.position[0]+40, master.position[1]+40))
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
                if not isinstance(obj, Bullet) and not isinstance(obj, type(self.master)):          # if bullet hits
                    try:                                                   # -> trying to call on_hit() for target(s)
                        obj.on_hit(self.damage)
                    except AttributeError:
                        pass
                    self.remove()                                                           # -> -> removing bullet
                    return
            return


class Wall(mwm.Token):
    def __init__(self, pos):
        super().__init__(pos)
        self.size = (tile_size[0], tile_size[1])

    def on_setup(self):
        self.add_image("images/wall.png")


class DestructibleWall(Wall):
    def on_setup(self):
        self.add_image("images/destructible_wall.png")

    def on_hit(self, damage):
        self.remove()


class Door(mwm.Token):
    def on_setup(self):
        self.add_image("")


class Coin(mwm.Token):
    def on_setup(self):
        self.add_image("images/coin.png")
        self.size = (80, 80)
        self.center_x += 10
        self.center_y += 10


class Enemy(mwm.Token):
    def on_setup(self):
        self.add_image("images/enemy.png")
        self.size = (80, 80)
        self.hp = 100
        self.damage = 50
        self.speed = 5
        self.move_buffer = 0  # time until next movement change (on setup always 0)
        self.turn_buffer = 0  # time until next direction change (on setup always 0)

    def act(self):
        self.random_movement()

    def random_movement(self):
        self.move_buffer -= d_time
        self.turn_buffer -= d_time
        if self.move_buffer <= 0:
            self.action = random.randint(0, 9)
            self.move_buffer = random.randint(2, 9)
        if self.turn_buffer <= 0:
            self.direction = random.randint(-180, 180)
            self.turn_buffer = random.randint(2, 9)
        if self.sensing_borders() or self.sensing_token(Wall):
            self.move_back()
            self.direction = random.randint(-180, 180)
        if self.action > 0:
            self.move()

    def on_hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.remove()
            return


def read_levels():
    global rooms
    rooms = list()
    for file in os.listdir("maps"):
        if file.endswith(".png"):
            rooms.append(Room())
            data = image.imread(f"maps/{file}")
            for y, line in enumerate(data):
                for x, col in enumerate(line):
                    col = [round(x, 1) for x in list(col)]
                    try:
                        rooms[len(rooms)-1].add_object(drawables[str(col)], [(x * tile_size[0], y * tile_size[1])])
                    except KeyError:
                        pass


res = (1600, 900)
tile_count_x = 16
tile_count_y = 9
tile_size = (100, 100)


d_time = 0
drawables = {
    "[0.0, 0.0, 1.0, 1.0]": Player, #rgba(0,0,255,255)
    "[0.0, 0.0, 0.0, 1.0]": Wall, #rgba(0,0,0,255)
    "[0.0, 0.5, 0.0, 1.0]": DestructibleWall, #rgba(0,~127,0,255)
    "[1.0, 0.8, 0.0, 1.0]": Coin, #rgba(255,~200,0,255)
    "[1.0, 0.0, 0.0, 1.0]": Enemy #rgma(255,0,0,255)
}

read_levels()
my_board = MyBoard(res[0], res[1])
my_board.show(fullscreen=True)
