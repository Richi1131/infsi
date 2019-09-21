import miniworldmaker as mwm
import time


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        player = Player((100, 100))


class Player(mwm.Actor):

    def on_setup(self):
        self.add_image("images/dog.png")
        self.costume.is_rotatable = False
        self.move_speed = 4
        self.shot_speed = 5
        self.shot_buffer = 0
        self.shot_cool = .5

    def on_key_pressed(self, key):
        if "a" in key:
            self.direction = -90
            self.move(self.move_speed)
        if "d" in key:
            self.direction = 90
            self.move(self.move_speed)
        if "w" in key:
            self.direction = 0
            self.move(self.move_speed)
        if "s" in key:
            self.direction = 180
            self.move(self.move_speed)
        if "left" in key:
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), -90, self.shot_speed)
                self.shot_buffer = self.shot_cool
        if "right" in key:
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), 90, self.shot_speed)
                self.shot_buffer = self.shot_cool
        if "up" in key:
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), 0, self.shot_speed)
                self.shot_buffer = self.shot_cool
        if "down" in key:
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), 180, self.shot_speed)
                self.shot_buffer = self.shot_cool

    def act(self):
        self.cool()

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
        self.add_image("images/monkey.png")
    
    def act(self):
        self.move(self.speed)


my_board = MyBoard(1000, 600)
my_board.show()
