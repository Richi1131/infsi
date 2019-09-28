import miniworldmaker as mwm
import time


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        player = Player((100, 100))
        Wall((200, 200))
        DestructibleWall((300, 300))


class Player(mwm.Actor):
    def on_setup(self):
        self.add_image("images/char.png")
        self.speed = 4    # character move speed
        self.shot_speed = 6    # bullet move speed
        self.shot_buffer = 0    # time till next shot (on setup always 0)
        self.shot_cool = .5    # time between shots

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
        if self.sensing_token(Wall, 100) is not None or self.sensing_borders() != []:
            self.move_back()

    def on_sensing_wall(self, wall):
        # additional collision to make glitches less common (not perfect)
        self.move_back()

    def shoot(self):
        if self.shot_buffer < 0:
            Bullet((self.position[0], self.position[1]), self.direction+self.costume.orientation, self.shot_speed)
            self.shot_buffer = self.shot_cool

    def cool(self):
        time_2 = time.time()
        try:
            d_time = time_2 - self.time
        except AttributeError:
            d_time = 0
        self.shot_buffer -= d_time
        self.time = time.time()


class Bullet(mwm.Token):
    def __init__(self, pos, direction, speed):
        super().__init__(pos)
        self.direction = direction
        self.speed = speed

    def on_setup(self):
        self.add_image("images/bullet.png")
        self.move(36)    # avoiding collision with player
    
    def act(self):
        self.move()
        if not self.sensing_on_board():
            self.remove()
            return
        if self.sensing_tokens() != [self]:     # if bullet hits
            for obj in self.sensing_tokens():   # -> trying to call on_hit() for target(s)
                if obj != self:                 # -> -> removing bullet
                    try:
                        obj.on_hit()
                    except AttributeError:
                        pass
            self.remove()
            return


class Wall(mwm.Token):
    def on_setup(self):
        self.add_image("images/wall.png")


class DestructibleWall(Wall):
    def on_setup(self):
        self.add_image("images/destructible_wall.png")

    def on_hit(self):
        self.remove()


my_board = MyBoard(1000, 600)
my_board.show()
