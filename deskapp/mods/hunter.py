import copy, random
import deskapp


class HunterGame:
    def __init__(self, starting_lives):
        self.starting_lives = starting_lives
        self.lives = starting_lives
        self.current_score = 0
        self.high_score = 10000
        self.speed = 0

        self.game_started = False
        self.game_paused = False
        self.game_over = False

        # self.gameboard = [[0 for _ in range(24)] for _ in range(24)]
        self.gameboard = []
        self.round = 0

        self.road_start = 6
        self.road_size = 10

        self.player_y = 5
        self.player_x = 5
        # self.show_player = True

    def generate_gameboard(self):
        for i in range(24):
            self.generate_next_line(i)
            self.move_road()
            self.round += 1

    def generate_next_line(self, line_no):
        line = []
        for i in range((self.road_size+2)-self.road_start):
            line.append('$')
        line.append('|')
        for i in range(self.road_size):
            line.append('.')
        line.append('|')
        for i in range(self.road_start):
            line.append('$')
        self.gameboard.append(line)

    def move_road(self):
        x = random.choice([0, 0, 0, 1, 2])
        if x == 1:
            if self.road_start > 0:
                self.road_start -= 1
        elif x == 2:
            if self.road_start < 12:
                self.road_start += 1

    def move_player(self, direction):
        if direction == 'down':
            if self.player_y > -4:
                self.player_y -= 1
        elif direction == 'up':
            if self.player_y < 17:
                self.player_y += 1
        elif direction == 'left':
            if self.player_x > -10:
                self.player_x -= 1
        elif direction == 'right':
            if self.player_x < 11:
                self.player_x += 1
    
    def start_game(self):
        self.game_started = True
        self.speed = 1

    def next_round(self):
        if not self.game_started: return
        if self.game_paused: return
        if not self.game_over:
            self.generate_next_line(self.round)
            self.move_road()
            self.round += 1

    def show_board(self, show_player=True):
        # t = list(self.gameboard.copy())
        output = copy.deepcopy(self.gameboard[-24:])
        if show_player:
            output[self.player_y+4][self.player_x+10] = '0'
            output[self.player_y+4][self.player_x+11] = '-'
            output[self.player_y+4][self.player_x+12] = '0'
            output[self.player_y+5][self.player_x+10] = '|'
            output[self.player_y+5][self.player_x+11] = '▦'
            output[self.player_y+5][self.player_x+12] = '|'
            output[self.player_y+6][self.player_x+10] = '0'
            output[self.player_y+6][self.player_x+11] = '-'
            output[self.player_y+6][self.player_x+12] = '0'

        output = [''.join(str(x) for x in line) for line in output]
        # q = self.gameboard[-24:]
        # qo = [''.join(str(x) for x in line) for line in q]
        return reversed(output)


class Deskhunter(deskapp.Module):
    name = "Test Drive"

    def __init__(self, app):
        super().__init__(app, "TestDrive")
        self.game = HunterGame(starting_lives=3)
        self.game.generate_gameboard()

    def update_header(self):
        header_string = f"DeskHunter - r:{self.game.round} | l:{self.game.lives} | s:{self.game.current_score} | h:{self.game.high_score}"
        self.app.set_header(header_string)

    def page(self, panel):
        self.game.next_round()
        self.update_header()
        self.write(panel, 0, 2, f"h: {self.h}, w: {self.w}")
        
        l=0
        for i, line in enumerate(self.game.show_board(True)):
            l = i
            self.write(panel, i+1, 0, line)

        self.write(panel, 1 + l, 2, f"Speed: {'Low ' if self.game.speed == 1 else ('High' if self.game.speed == 2 else 'Off ')}")

    @deskapp.callback("TestDrive", deskapp.Keys.SPACE)
    def on_space(self, *args, **kwargs):
        self.print("paused")
        if not self.game.game_started: return
        self.game.game_paused = not self.game.game_paused

    @deskapp.callback("TestDrive", deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.game.game_over:
            self.game = Deskhunter(starting_lives=3)
            self.game.generate_gameboard()
            self.print("Game restarted")
        else:
            if self.game.game_started:
                self.game.game_over = True
                self.print("Game over")
            else:
                self.game.start_game()
                self.print("Game started")

    @deskapp.callback("TestDrive", deskapp.Keys.UP)
    def on_up(self, *args, **kwargs):
        self.game.move_player('up')

    @deskapp.callback("TestDrive", deskapp.Keys.DOWN)
    def on_down(self, *args, **kwargs):
        self.game.move_player('down')

    @deskapp.callback("TestDrive", deskapp.Keys.LEFT)
    def on_left(self, *args, **kwargs):
        self.game.move_player('left')

    @deskapp.callback("TestDrive", deskapp.Keys.RIGHT)
    def on_right(self, *args, **kwargs):
        self.game.move_player('right')