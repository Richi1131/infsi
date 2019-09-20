import miniworldmaker as mwm

class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/backgroundCastles.png")
        player = Player((100,100))
       

class Player(mwm.Actor):
        
    def on_setup(self):
        self.add_image("images/dog.png")
        self.costume.is_rotatable = False
        self.move_speed = 4
    
    def on_key_pressed(self, key):
        if "a" in key:
            self.direction = -90
            #self.costume.orientation = -self.direction
            self.move(self.move_speed)
        if "d" in key:
            self.direction = 90
            #self.costume.orientation = -self.direction
            self.move(self.move_speed)
        if "w" in key:
            self.direction = 0
            #self.costume.orientation = 0
            self.move(self.move_speed)
        if "s" in key:
            self.direction = 180
            #self.costume.orientation = 180
            self.move(self.move_speed)


class Bullet(mwm.Token):
    def __init__(self, direction, speed):
        self.direction = direction
        self.speed = speed
        
    def on_setup(self):
        self.add_image("images/monkey.png")
    
    def act():
    
my_board = MyBoard(1000, 600)
my_board.show()