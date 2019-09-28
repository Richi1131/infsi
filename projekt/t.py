import miniworldmaker as mwm
import time


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        self.player = Player((100, 100))
        Wall((200, 200))
        DestructibleWall((300, 300))
        Enemy((400, 400))


class Player(mwm.Actor):
    def on_setup(self):
        self.add_image("images/char.png")
        self.speed = 4    # character move speed
        self.hp = 100    # character hit points
        self.shot_speed = 6    # bullet move speed
        self.shot_cool = .5    # time between shots
        self.damage = 50
        self.shot_buffer = 0    # time till next shot (on setup always 0)
        self.damage_buffer = 0    # time till able to take damage (on setup always 0)

    def on_key_pressed(self, key):
        # movement
        if "a" in key:
            self.direction = -90
            self.move()
        elif "d" in key:
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
            self.costume.orientation = -self.direction - 90
            self.shoot()
        elif "right" in key:
            self.costume.orientation = -self.direction + 90
            self.shoot()
        elif "up" in key:
            self.costume.orientation = -self.direction
            self.shoot()
        elif "down" in key:
            self.costume.orientation = -self.direction + 180
            self.shoot()
        else:
            self.costume.orientation = 0

    def act(self):
        self.cool()   # reducing shot cooldown
        # collision (walls and borders)
        if self.sensing_token(Wall, 100) or self.sensing_borders() != []:
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

    def shoot(self):
        if self.shot_buffer <= 0:
            Bullet(self)
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
    def __init__(self, master):
        self.master = master
        super().__init__(master.position)
        if type(master) == Player:
            self.direction = master.direction + master.costume.orientation
        else:
            self.direction = master.direction
        self.speed = master.shot_speed
        self.damage = master.damage

    def on_setup(self):
        self.add_image("images/bullet.png")

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



my_board = MyBoard(1000, 600)
my_board.show()
