import miniworldmaker as mwm
import time


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        player = Player((100, 100))
        Wall((200, 200))


class Player(mwm.Actor):

    def on_setup(self):
        self.add_image("images/dog.png")
        self.move_speed = 4
        self.shot_speed = 5
        self.shot_buffer = 0
        self.shot_cool = .5

    def on_key_pressed(self, key):
        if "a" in key:
            self.direction = -90
            if not self.blocked:
                self.move(self.move_speed)
        elif "d" in key:
            self.direction = 90
            if not self.blocked:
                self.move(self.move_speed)
        elif "w" in key:
            self.direction = 0
            if not self.blocked:
                self.move(self.move_speed)
        elif "s" in key:
            self.direction = 180
            if not self.blocked:
                self.move(self.move_speed)
        if "left" in key:
            self.costume.orientation = -self.direction - 90
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), -90, self.shot_speed)
                self.shot_buffer = self.shot_cool
        elif "right" in key:
            self.costume.orientation = -self.direction + 90
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), 90, self.shot_speed)
                self.shot_buffer = self.shot_cool
        elif "up" in key:
            self.costume.orientation = -self.direction
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), 0, self.shot_speed)
                self.shot_buffer = self.shot_cool
        elif "down" in key:
            self.costume.orientation = -self.direction + 180
            if self.shot_buffer < 0:
                Bullet((self.position[0], self.position[1]), 180, self.shot_speed)
                self.shot_buffer = self.shot_cool
        else:
            self.costume.orientation = 0
        

    def act(self):
        self.cool()
        if self.sensing_tokens(5, Wall) != [] or self.sensing_borders() != []:
            self.blocked = True
        else:
            self.blocked = False
        print(self.sensing_tokens(5, Wall), self.sensing_borders())

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
        
    def not_board(self):
        self.remove()
        

class Wall(mwm.Token):

    def on_setup(self):
        self.add_image("images/cow.png")

my_board = MyBoard(1000, 600)
my_board.show()
