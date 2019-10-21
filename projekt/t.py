import miniworldmaker as mwm
import time
import pygame


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        self.player = Player((100, 100))
        Wall((0, 0))
        DestructibleWall((50, 0))
        Enemy((400, 400))
        self.set_room(rooms[0])

    def on_key_pressed(self, key):
        if "f11" in key:
            self.reset()

    def load_room(self):
        for token in self.get_tokens_at_rect((pygame.Rect(0, 0, 1600, 900))):
            token.remove()
        for object in self.room.content:
            for pos in object.positions:
                object.type((pos[0]*50, pos[1]*50))
        Player((0, 430))

    def set_room(self, room):
        self.room = room
        self.load_room()


class Room:
    def __init__(self, content: list):
        self.content = content


class RoomObject:
    def __init__(self, type, positions: list):
        self.type = type
        self.positions = positions


class Player(mwm.Actor):
    def on_setup(self):
        self.add_image("images/char.png")
        self.speed = 4    # character move speed
        self.hp = 100    # character hit points
        self.shot_speed = 5    # bullet move speed
        self.shot_cool = .5    # time between shots
        self.damage = 50    # character damage per shot
        self.shot_buffer = 0    # time till next shot (on setup always 0)
        self.damage_buffer = 0    # time till able to take damage (on setup always 0)

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
        self.cool()   # reducing shot cooldown
        # collision (walls and borders)
        if self.sensing_token(Wall, 1) or self.sensing_borders() != []:
            self.move_back()
        # collision with enemies
        if self.sensing_token(Enemy, 1):
            self.on_hit(self.sensing_token(Enemy, 1).damage)

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
        super().__init__((master.position[0]+10, master.position[1]+10))
        self.direction = direction
        self.speed = master.shot_speed
        self.damage = master.damage

    def on_setup(self):
        self.add_image("images/bullet.png")
        self.size = (10, 10)

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
                    self.remove()                                                             # -> -> removing bullet
            return


class Wall(mwm.Token):
    def __init__(self, pos):
        super().__init__(pos)
        self.size = (50, 50)
    def on_setup(self):
        self.add_image("images/wall.png")


class DestructibleWall(Wall):
    def on_setup(self):
        self.add_image("images/destructible_wall.png")

    def on_hit(self, damage):
        self.remove()


class Enemy(mwm.Token):
    def on_setup(self):
        self.add_image("images/enemy.png")
        self.hp = 100
        self.damage = 50

    def on_hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.remove()
            return
    

def main():
    my_board = MyBoard(1600, 900)
    my_board.show(fullscreen=True)

rooms = [
    Room([RoomObject(Wall, [(x, 1) for x in range(1, 30)])])
]

main()
