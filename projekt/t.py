import miniworldmaker as mwm
import time
import pygame
import matplotlib.image as image
import os
import random


class MyBoard(mwm.PixelBoard):
    def on_setup(self):
        self.add_image("images/background.png")
        self.load_menu()
        self._last_time = None
        self.gui_health = list()
        self.gui_bombs = list()
        self.gui_coins = list()
        # defining how frequent special rooms appear (every n-th room counting from 0)
        self.boss_infrequency = 10
        self.shop_infrequency = 5

    def act(self):
        # calculating time past since last frame
        global d_time
        current_time = time.time()
        if self._last_time is None:
            d_time = 0
        else:
            d_time = current_time - self._last_time

        self._last_time = time.time()

    def on_key_down(self, key):
        if "SPACE" in key and self.in_menu:
            # reseting savedata
            global coins, bombs, health, player_speed, player_shot_cool, player_damage, clean_run, start_time
            coins = 0
            bombs = 0
            health = 2
            player_speed = 5
            player_shot_cool = 0.5
            player_damage = 1
            clean_run = True
            start_time = time.time()
            self.set_level(0)
        if "F11" in key:
            self.load_menu()
        if "ESC" in key and self.in_menu:
            raise GameExit("Let me out!")


    def load_menu(self):
        self.clear()
        self.play_music("sounds/music.wav")
        self.in_menu = True
        mwm.TextToken(position=(650, 300), font_size=50, color=(0, 0, 0, 255), text="Platzhalter")
        mwm.TextToken(position=(650, 800), font_size=20, color=(0, 0, 0, 255), text="Press SPACEBAR to start")

    def load_room(self):
        self.clear()
        self.in_menu = False
        self.enemy_count = 0
        # placing objects
        for object in self.room.content:
            for pos in object.positions:
                if object.type == Player:
                    self.player = Player(pos)
                else:
                    object.type(pos)
                    if object.type == Enemy:
                        self.enemy_count += 1
        self.load_gui()

    def clear(self):
        for token in self.get_tokens_at_rect((pygame.Rect(0, 0, res[0], res[1]))):
            token.remove()
            self.gui_health = list()
            self.gui_bombs = list()
            self.gui_coins = list()

    def load_gui(self):
        global coins, bombs, health
        # removing old gui
        [x.remove() for x in self.gui_health]
        [x.remove() for x in self.gui_bombs]
        [x.remove() for x in self.gui_coins]
        # placing new gui
        self.gui_health = [GuiHeart((x%10*50+25, x//10*50)) for x in range(health)]
        self.gui_bombs = [GuiBomb((x%10*50+550, x//10*50)) for x in range(bombs)]
        self.gui_coins = [GuiCoin((x%10*50+1075, x//10*50)) for x in range(coins)]

    def _set_room(self, room):
        self.room = room
        self.load_room()

    def _sync_room_to_level(self):
        try:
            # determining which type of room needs to be loaded
            if self.level != 0 and self.level % self.boss_infrequency == 0:
                self._set_room(boss_rooms[self.level // self.boss_infrequency - 1])

            elif self.level != 0 and self.level % self.shop_infrequency == 0:
                self._set_room(shop_rooms[0])

            else:

                self._set_room(rooms[self.level-(self.level//self.boss_infrequency)-(self.level//self.shop_infrequency)])
                # ^^ making sure no level gets skipped, because a special one was loaded instead ^^
        except IndexError:
            # no levels remain -> you win
            self.win()

    def set_level(self, level):
        self.level = level
        self._sync_room_to_level()

    def inc_level(self):
        self.level += 1
        self._sync_room_to_level()

    def win(self):
        self.clear()
        run_time = time.time() - start_time
        self.in_menu = True
        mwm.TextToken(position=(650, 100), font_size=50, color=(0, 0, 0, 255), text="You Won!")
        mwm.TextToken(position=(200, 300), font_size=25, color=(0, 0, 0, 255), text=f"{round(100000//run_time)} pints from the {run_time} seconds you took.")
        mwm.TextToken(position=(200, 350), font_size=25, color=(0, 0, 0, 255), text=f"{coins*10} points fom the {coins} coins you had left over.")
        mwm.TextToken(position=(200, 400), font_size=25, color=(0, 0, 0, 255), text=f"{health*10} points fom the {health} hearts you had left over.")
        mwm.TextToken(position=(200, 450), font_size=25, color=(0, 0, 0, 255), text=f"TOTAL SCORE: {round(100000//run_time+coins*10+health*10)}")

    def loose(self):
        self.clear()
        self.in_menu = True
        mwm.TextToken(position=(650, 400), font_size=50, color=(0, 0, 0, 255), text="You Loose!")

    def in_shop(self):
        return self.room in shop_rooms


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


class GuiHeart(mwm.Token):
    def on_setup(self):
        self.add_image("images/gui_heart.png")
        self.size = (50, 50)


class GuiBomb(mwm.Token):
    def on_setup(self):
        self.add_image("images/gui_bomb.png")
        self.size = (40, 50)


class GuiCoin(mwm.Token):
    def on_setup(self):
        self.add_image("images/gui_coin.png")
        self.size = (40, 40)


class Player(mwm.Actor):
    def on_setup(self):
        self.add_image("images/char.png")
        global player_speed, player_shot_cool, player_damage
        self.speed = player_speed  # character move speed
        self.shot_speed = 10  # bullet move speed
        self.shot_cool = player_shot_cool  # time between shots
        self.damage = player_damage  # character damage per shot
        self.shot_buffer = 0  # time till next shot (on setup always 0)
        self.damage_buffer = 0  # time till able to take damage (on setup always 0)
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
            self.shoot(-90)
        elif "right" in key:
            self.shoot(90)
        elif "up" in key:
            self.shoot(0)
        elif "down" in key:
            self.shoot(180)
        else:
            self.costume.orientation = 0

    def on_key_down(self, key):
        # placing bombs
        if "e" in key:
            global bombs
            if bombs > 0:
                BombExploding((self.position[0] - 60, self.position[1] - 60))
                bombs -= 1
                self.board.gui_bombs[-1].remove()
                self.board.gui_bombs.pop(len(self.board.gui_bombs)-1)
        elif "p" in key:
            try:
                self.sensing_token(Wall, 1).remove()
                global clean_run
                clean_run = False
            except AttributeError:
                pass

    def act(self):
        # collision (walls and borders)
        if self.sensing_token(Wall, 1) or self.sensing_borders() != []:
            self.move_back()
        # taking damage from enemies
        if self.sensing_token(Enemy, 1):
            self.on_hit(self.sensing_token(Enemy, 1).damage)
        # interacting with items
        for token in self.sensing_tokens(Item, 1):
            token.on_touch()
        # reducing cooldowns
        if self.shot_buffer > 0:
            self.shot_buffer -= d_time
        if self.damage_buffer > 0:
            self.damage_buffer -= d_time

    def on_sensing_wall(self, wall):
        # additional collision to make glitches less common (not perfect)
        self.move_back()

    def on_hit(self, damage):
        global health
        if self.damage_buffer <= 0:
            health -= damage
            self.damage_buffer = 1
            if health <= 0:
                self.board.loose()
                return
            else:
                for i in range(damage):
                    self.board.gui_health[-1].remove()
                    self.board.gui_health.pop(len(self.board.gui_health)-1)

    def on_blast(self):
        self.on_hit(5)

    def shoot(self, direction):
        if self.shot_buffer <= 0:
            self.board.play_sound("sounds/shot.wav")
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
                if not isinstance(obj, type(self.master)) and\
                        (isinstance(obj, Enemy) or isinstance(obj, Wall or isinstance(obj, Player))):
                    try:  # ^ if bullet hits
                        obj.on_hit(self.damage)  # -> trying to call on_hit() for target(s)
                    except AttributeError:
                        pass
                    self.remove()  # -> -> removing bullet
                    return
            return


class Wall(mwm.Token):
    def __init__(self, pos):
        super().__init__(pos)
        self.size = (100, 100)

    def on_setup(self):
        self.add_image("images/wall.png")

    def on_blast(self):
        self.remove()


class DestructibleWall(Wall):
    def on_setup(self):
        self.add_image("images/destructible_wall.png")

    def on_hit(self, damage):
        self.board.play_sound("sounds/wall_break.wav")
        self.remove()


class Item(mwm.Token):
    # parent class, not meant to be instanced
    def on_setup(self):
        self.price = 0

    def on_blast(self):
        self.remove()

    def on_touch(self):
        pass

    def on_in_shop(self):
        if self.price > 0:
            self.gui_price = [GuiCoin((self.position[0]-(self.price*30-20)+x*50, self.position[1]-95))
                              for x in range(self.price)]


class ExitLocation(mwm.Token):
    def on_setup(self):
        self.size = (100, 100)
        self.add_image("images/empty.png")

    def act(self):
        # adding exit once no enemies are left
        if my_board.enemy_count == 0:
            Exit((self.position[0] - 50, self.position[1] - 50))
            self.remove()


class ItemLocation(mwm.Token):
    def on_setup(self):
        global buyables
        buyables[random.randint(0, len(buyables)-1)](self.position)
        self.remove()


class Exit(Item):
    def on_setup(self):
        self.size = (100, 100)
        self.add_image("images/exit.png")
        # making it look nice
        if self.position[1] <= 50:
            self.direction = 180
        elif self.position[0] <= 50:
            self.direction = 90
        elif self.position[0] >= 1550:
            self.direction = -90

    def on_touch(self):
        self.board.inc_level()

    def on_blast(self):
        pass


class Coin(Item):
    def on_setup(self):
        self.add_image("images/coin.png")
        self.size = (80, 80)
        self.position = (self.position[0] + 10, self.position[1] + 10)

    def on_touch(self):
        self.board.play_sound("sounds/collect_coin.wav")
        global coins
        coins += 1
        self.board.load_gui()
        self.remove()


class Heart(Item):
    def on_setup(self):
        self.add_image("images/heart.png")
        self.size = (80, 80)
        self.position = (self.position[0] + 10, self.position[1] + 10)

        self.price = 2
        if self.board.in_shop():
            self.on_in_shop()

    def on_touch(self):
        global health, coins
        # buying hearts
        if self.board.in_shop():
            if coins >= self.price:
                self.board.play_sound("sounds/collect_boost.wav")
                health += 1
                coins -= self.price
                self.board.load_gui()
                [self.gui_price[x].remove() for x in range(len(self.gui_price))]
                self.remove()
        # collecting hearts
        else:
            self.board.play_sound("sounds/collect_boost.wav")
            health += 1
            self.board.load_gui()
            self.remove()


class BombItem(Item):
    def on_setup(self):
        self.add_image("images/bomb_item.png")
        self.size = (100, 100)

        self.price = 2
        if self.board.in_shop():
            self.on_in_shop()

    def on_blast(self):
        self.board.play_sound("sounds/explosion.wav")
        Explosion0((self.position[0] - 150, self.position[1] - 150))
        self.remove()

    def on_touch(self):
        global bombs, coins
        # buying bombs
        if self.board.in_shop():
            if coins >= self.price:
                self.board.play_sound("sounds/collect_bomb.wav")
                bombs += 1
                coins -= self.price
                self.board.load_gui()
                [self.gui_price[x].remove() for x in range(len(self.gui_price))]
                self.remove()
        # collecting bombs
        else:
            self.board.play_sound("sounds/collect_bomb.wav")
            bombs += 1
            self.board.load_gui()
            self.remove()


class BoostSpeed(Item):
    def on_setup(self):
        self.add_image("images/boost_speed.png")
        self.size = (80, 80)
        self.position = (self.position[0] + 10, self.position[1] + 10)
        self.price = 3
        if self.board.in_shop():
            self.on_in_shop()

    def on_touch(self):
        global coins, player_speed
        # buying speed boosts
        if self.board.in_shop():
            if coins >= self.price:
                self.board.play_sound("sounds/collect_boost.wav")
                self.board.player.speed += 1
                player_speed += 1
                coins -= self.price
                self.board.load_gui()
                [self.gui_price[x].remove() for x in range(len(self.gui_price))]
                self.remove()
        # collecting speed boosts
        else:
            self.board.play_sound("sounds/collect_boost.wav")
            self.board.player.speed += 1
            player_speed += 1
            self.board.load_gui()
            self.remove()


class BoostFireRate(Item):
    def on_setup(self):
        self.add_image("images/boost_fire_rate.png")
        self.size = (80, 80)
        self.position = (self.position[0] + 10, self.position[1] + 10)
        self.price = 3
        if self.board.in_shop():
            self.on_in_shop()

    def on_touch(self):
        global coins, player_shot_cool
        if self.board.in_shop():
            if coins >= self.price:
                self.board.play_sound("sounds/collect_boost.wav")
                self.board.player.shot_cool *= 0.8
                player_shot_cool *= 0.8
                coins -= self.price
                self.board.load_gui()
                [self.gui_price[x].remove() for x in range(len(self.gui_price))]
                self.remove()
        else:
            self.board.play_sound("sounds/collect_boost.wav")
            self.board.player.shot_cool *= 0.8
            player_shot_cool *= 0.8
            self.board.load_gui()
            self.remove()


class BoostDamage(Item):
    def on_setup(self):
        self.add_image("images/boost_damage.png")
        self.size = (80, 80)
        self.position = (self.position[0] + 10, self.position[1] + 10)
        self.price = 4
        if self.board.in_shop():
            self.on_in_shop()

    def on_touch(self):
        global coins, player_damage
        # buying speed boosts
        if self.board.in_shop():
            if coins >= self.price:
                self.board.play_sound("sounds/collect_boost.wav")
                self.board.player.damage += 1
                player_damage += 1
                coins -= self.price
                self.board.load_gui()
                [self.gui_price[x].remove() for x in range(len(self.gui_price))]
                self.remove()
        # collecting speed boosts
        else:
            self.board.play_sound("sounds/collect_boost.wav")
            self.board.player.damage += 1
            player_damage += 1
            self.board.load_gui()
            self.remove()


class BombExploding(mwm.Token):
    def on_setup(self):
        self.add_image("images/bomb_exploding.png")
        self.size = (100, 100)
        self.explosion_buffer = 1.2

    def act(self):
        if self.explosion_buffer < 0:
            self.board.play_sound("sounds/explosion.wav")
            Explosion0((self.position[0] - 150, self.position[1] - 150))
            self.remove()
            return
        else:
            self.explosion_buffer -= d_time


class Explosion(mwm.Token):
    def on_setup(self):
        self.size = (300, 300)
        self.remove_buffer = 0
        self.next_exposion = None
        self.damaging = False

    def act(self):
        if self.remove_buffer < 0:
            try:
                self.next_exposion((self.position[0] - 150, self.position[1] - 150))
            except TypeError:
                pass
            self.remove()
            return
        if self.damaging:
            for token in self.sensing_tokens():
                try:
                    token.on_blast()
                except AttributeError:
                    pass
        self.remove_buffer -= d_time


class Explosion0(Explosion):
    def on_setup(self):
        self.add_image("images/explosion_0.png")
        self.size = (300, 300)
        self.remove_buffer = 0.1
        self.next_exposion = Explosion1
        self.damaging = True


class Explosion1(Explosion):
    def on_setup(self):
        self.add_image("images/explosion_1.png")
        self.size = (300, 300)
        self.remove_buffer = 0.1
        self.next_exposion = Explosion2
        self.damaging = True


class Explosion2(Explosion):
    def on_setup(self):
        self.add_image("images/explosion_2.png")
        self.size = (300, 300)
        self.remove_buffer = 0.5
        self.next_exposion = Explosion3
        self.damaging = False


class Explosion3(Explosion):
    def on_setup(self):
        self.add_image("images/explosion_3.png")
        self.size = (300, 300)
        self.remove_buffer = 0.5
        self.next_exposion = None
        self.damaging = False


class Enemy(mwm.Token):
    def on_setup(self):
        self.add_image("images/enemy.png")
        self.size = (80, 80)
        self.position = (self.position[0] + 10, self.position[1] + 10)
        self.hp = 2 + self.board.level//10
        self.damage = 1 + self.board.level//10
        self.speed = 4
        self.target_position = None
        self.move_buffer = 0

    def act(self):
        if self.sensing_token(Wall, 1) or self.sensing_borders() != []:
            self.move_back()
        self.target_position = self.board.player.position
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


class GameExit(Exception):
    pass


def read_levels():
    global rooms, boss_rooms, shop_rooms
    rooms = list()
    build_levels("maps", rooms)

    boss_rooms = list()
    build_levels("maps/boss", boss_rooms)

    shop_rooms = list()
    build_levels("maps/shop", shop_rooms)


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
                        save_location[len(save_location) - 1].add_object(drawables[str(col)], [(x * tile_size[0], y * tile_size[1])])
                    except KeyError:
                        pass


res = (1600, 900)
tile_size = (100, 100)

d_time = 0

drawables = {
    "[0.0, 0.0, 1.0, 1.0]": Player,             # RGBA(0,0,255,255)
    "[0.0, 0.0, 0.0, 1.0]": Wall,               # RGBA(0,0,0,255)
    "[0.0, 0.5, 0.0, 1.0]": DestructibleWall,   # RGBA(0,~127,0,255)
    "[1.0, 0.8, 0.0, 1.0]": Coin,               # RGBA(255,~200,0,255)
    "[1.0, 0.0, 0.0, 1.0]": Enemy,              # RGBA(255,0,0,255)
    "[0.5, 0.5, 0.0, 1.0]": ExitLocation,       # RGBA(~127,~127,0,255)
    "[0.5, 0.5, 0.5, 1.0]": BombItem,           # RGBA(~127,~127,~127,255)
    "[0.5, 0.0, 0.0, 1.0]": Heart,              # RGBA(~127,0,0,255)
    "[1.0, 1.0, 1.0, 1.0]": ItemLocation        # RGBA(255,255,255,255)
}
buyables = [BombItem, Heart, BoostSpeed, BoostFireRate, BoostDamage]

read_levels()
my_board = MyBoard(res[0], res[1])
my_board.show(fullscreen=True)
