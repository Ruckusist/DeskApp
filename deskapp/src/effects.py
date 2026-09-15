import time
import random

class ColorPalette:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.named_colors = {
                "yellow": getattr(app.front, "color_yellow", 0),
                "red": getattr(app.front, "color_red", 0),
                "green": getattr(app.front, "color_green", 0),
                "blue": getattr(app.front, "color_blue", 0),
                "black": getattr(app.front, "color_black", 0),
                "cyan": getattr(app.front, "color_cyan", 0),
                "white": getattr(app.front, "color_white", 0),
                "magenta": getattr(app.front, "color_magenta", 0),
                "bold": getattr(app.front, "color_bold", 0),
                "dim": getattr(app.front, "color_dim", 0),
                "error": getattr(app.front, "color_error", 0),
            }
        else:
            self.named_colors = {}

    def PaletteIndex(self, index):
        if not self.app or not hasattr(self.app.front, "palette") or not self.app.front.palette:
            return 0
        idx = max(0, min(index, len(self.app.front.palette) - 1))
        return self.app.front.palette[idx]

    def Gradient(self, color_a, color_b, steps):
        gradient = []
        for i in range(steps):
            if i < steps // 2:
                gradient.append(color_a)
            else:
                gradient.append(color_b)
        return gradient

    def CycleColors(self, colors, frame, speed):
        idx = int(frame * speed) % len(colors)
        return colors[idx]

class BaseEffect:
    def __init__(self, Text, Row=0, Col=0, Speed=1.0, Loop=False, HoldFinal=True, ShowCursor=False, CursorChar="_", clock=time.monotonic):
        self.Text = Text
        self.Row = Row
        self.Col = Col
        self.Speed = Speed
        self.Loop = Loop
        self.HoldFinal = HoldFinal
        self.ShowCursor = ShowCursor
        self.CursorChar = CursorChar
        self.clock = clock
        
        self.start_time = 0
        self.elapsed = 0
        self.is_active = False
        self.is_done = False
        
        self.previous_cells = set()
        
    @property
    def IsActive(self):
        return self.is_active

    @property
    def IsDone(self):
        return self.is_done

    def Start(self):
        self.start_time = self.clock()
        self.elapsed = 0
        self.is_active = True
        self.is_done = False
        self.previous_cells = set()

    def Stop(self):
        self.is_active = False

    def Reset(self):
        self.start_time = self.clock()
        self.elapsed = 0
        self.is_active = False
        self.is_done = False
        self.previous_cells = set()

    def Update(self):
        if self.is_active:
            self.elapsed = self.clock() - self.start_time

    def clear_previous_cells(self, mod, panel, current_cells):
        cells_to_clear = self.previous_cells - current_cells
        for r, c in cells_to_clear:
            mod.write(panel, r, c, " ", attr=0)
        self.previous_cells = current_cells

    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        pass


class TypewriterEffect(BaseEffect):
    def __init__(self, Text, Row=0, Col=0, Speed=10.0, Loop=False, HoldFinal=True, ShowCursor=True, CursorChar="_", clock=time.monotonic):
        super().__init__(Text, Row, Col, Speed, Loop, HoldFinal, ShowCursor, CursorChar, clock)

    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_cells = set()
        
        if not self.is_active and not (self.is_done and self.HoldFinal):
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        chars_to_show = int(self.elapsed * self.Speed)
        
        if chars_to_show >= len(self.Text):
            chars_to_show = len(self.Text)
            if self.Loop:
                self.start_time = self.clock()
            else:
                self.is_done = True
                self.is_active = False

        text_to_show = self.Text[:chars_to_show]
        
        cursor = ""
        if self.ShowCursor and self.is_active:
            if int(self.elapsed * 2) % 2 == 0:
                cursor = self.CursorChar
                
        full_text = text_to_show + cursor
        
        for i, char in enumerate(full_text):
            current_cells.add((row, col + i))
            
        self.clear_previous_cells(Mod, Panel, current_cells)
        Mod.write(Panel, row, col, full_text)


class PulseEffect(BaseEffect):
    def __init__(self, Text, Row=0, Col=0, Speed=2.0, Loop=True, HoldFinal=True, Colors=None, clock=time.monotonic):
        super().__init__(Text, Row, Col, Speed, Loop, HoldFinal, False, "", clock)
        self.Colors = Colors or ["white", "yellow", "red", "magenta", "blue", "cyan", "green"]

    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_cells = set()
        
        if not self.is_active and not (self.is_done and self.HoldFinal):
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        color_idx = int(self.elapsed * self.Speed)
        
        if not self.Loop and color_idx >= len(self.Colors):
            color_idx = len(self.Colors) - 1
            self.is_done = True
            self.is_active = False
            
        color_idx = color_idx % len(self.Colors)
        current_color = self.Colors[color_idx]
        
        for i, char in enumerate(self.Text):
            current_cells.add((row, col + i))
            
        self.clear_previous_cells(Mod, Panel, current_cells)
        Mod.write(Panel, row, col, self.Text, color=current_color)


class DissolveEffect(BaseEffect):
    def __init__(self, Text, Row=0, Col=0, Speed=5.0, Charset=None, Seed=None, clock=time.monotonic):
        super().__init__(Text, Row, Col, Speed, False, True, False, "", clock)
        self.Charset = Charset or [" ", ",", "^", "~", "*", "|", "H", "$", "#", "@"]
        self.rng = random.Random(Seed)
        
    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_cells = set()
        
        if not self.is_active and not (self.is_done and self.HoldFinal):
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        stage = int(self.elapsed * self.Speed)
        max_stage = len(self.Charset)
        
        if stage >= max_stage:
            stage = max_stage
            self.is_done = True
            self.is_active = False

        self.rng.seed(hash(self.Text) + stage)
        
        dissolved_text = ""
        for char in self.Text:
            if stage == max_stage:
                dissolved_text += " "
            elif stage > 0 and self.rng.random() < (stage / max_stage):
                dissolved_text += self.rng.choice(self.Charset)
            else:
                dissolved_text += char
                
        for i, char in enumerate(dissolved_text):
            if char != " ":
                current_cells.add((row, col + i))
                
        self.clear_previous_cells(Mod, Panel, current_cells)
        Mod.write(Panel, row, col, dissolved_text)


class MatrixRainEffect(BaseEffect):
    def __init__(self, Row=0, Col=0, Width=10, Height=10, Speed=15.0, Seed=None, clock=time.monotonic):
        super().__init__("", Row, Col, Speed, True, False, False, "", clock)
        self.Width = Width
        self.Height = Height
        self.rng = random.Random(Seed)
        self.seed = Seed if Seed is not None else random.randint(0, 10000)

    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        h = Height if Height is not None else self.Height
        w = Width if Width is not None else self.Width
        
        current_cells = set()
        
        if not self.is_active:
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        ticks = int(self.elapsed * self.Speed)
        
        c_white = getattr(Mod.front, "color_white", 0)
        c_green = getattr(Mod.front, "color_green", 0)
        
        for c in range(w):
            self.rng.seed(self.seed + c)
            col_speed = self.rng.uniform(0.5, 1.5)
            col_offset = self.rng.randint(0, 100)
            drop_len = self.rng.randint(3, h)
            
            head_y = int(ticks * col_speed + col_offset) % (h + drop_len) - drop_len
            
            for i in range(drop_len):
                y = head_y + i
                if 0 <= y < h:
                    current_cells.add((row + y, col + c))
                    if i == drop_len - 1:
                        attr = c_white
                    else:
                        attr = c_green
                        
                    char = chr(self.rng.randint(33, 126))
                    Mod.write(Panel, row + y, col + c, char, attr=attr)
                    
        self.clear_previous_cells(Mod, Panel, current_cells)


class BigText:
    def __init__(self, Text, Row=0, Col=0, FillChar=None):
        self.Text = Text
        self.Row = Row
        self.Col = Col
        self.FillChar = FillChar
        self.glyphs = {
            '0': [" 000 ", "0   0", "0   0", "0   0", " 000 "],
            '1': ["  1  ", " 11  ", "  1  ", "  1  ", " 111 "],
            '2': [" 222 ", "2   2", "   2 ", "  2  ", "22222"],
            '3': [" 333 ", "3   3", "  33 ", "3   3", " 333 "],
            '4': ["   4 ", "  44 ", " 4 4 ", "44444", "   4 "],
            '5': ["55555", "5    ", "5555 ", "    5", "5555 "],
            '6': [" 666 ", "6    ", "6666 ", "6   6", " 666 "],
            '7': ["77777", "    7", "   7 ", "  7  ", " 7   "],
            '8': [" 888 ", "8   8", " 888 ", "8   8", " 888 "],
            '9': [" 999 ", "9   9", " 9999", "    9", " 999 "],
            ':': ["   ", " . ", "   ", " . ", "   "],
            ' ': ["   ", "   ", "   ", "   ", "   "]
        }
        
    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None, Color=None, Attr=None, Scale=1):
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_col = col
        for char in self.Text:
            if char in self.glyphs:
                glyph = self.glyphs[char]
            else:
                glyph = ["     "] * 5
                
            for r, line in enumerate(glyph):
                render_line = line
                if self.FillChar:
                    render_line = "".join([self.FillChar if c != " " else " " for c in line])
                    
                if Attr is not None:
                    Mod.write(Panel, row + r, current_col, render_line, attr=Attr)
                else:
                    Mod.write(Panel, row + r, current_col, render_line, color=Color)
                    
            current_col += len(glyph[0]) + 1


class HugeText:
    def __init__(self, Text, Row=0, Col=0, FillChar=None):
        self.Text = Text
        self.Row = Row
        self.Col = Col
        self.FillChar = FillChar
        self.glyphs = {
            '0': ["  000  ", " 0   0 ", " 0   0 ", " 0   0 ", " 0   0 ", " 0   0 ", "  000  "],
            '1': ["   1   ", "  11   ", " 1 1   ", "   1   ", "   1   ", "   1   ", " 11111 "],
            '2': ["  222  ", " 2   2 ", "     2 ", "   22  ", "  2    ", " 2     ", " 22222 "],
            '3': ["  333  ", " 3   3 ", "     3 ", "   33  ", "     3 ", " 3   3 ", "  333  "],
            '4': ["    4  ", "   44  ", "  4 4  ", " 4  4  ", " 44444 ", "    4  ", "    4  "],
            '5': [" 55555 ", " 5     ", " 5555  ", "     5 ", "     5 ", " 5   5 ", "  555  "],
            '6': ["  666  ", " 6     ", " 6     ", " 6666  ", " 6   6 ", " 6   6 ", "  666  "],
            '7': [" 77777 ", "     7 ", "    7  ", "   7   ", "  7    ", "  7    ", "  7    "],
            '8': ["  888  ", " 8   8 ", " 8   8 ", "  888  ", " 8   8 ", " 8   8 ", "  888  "],
            '9': ["  999  ", " 9   9 ", " 9   9 ", "  9999 ", "     9 ", "     9 ", "  999  "],
            ':': ["       ", "   .   ", "   .   ", "       ", "   .   ", "   .   ", "       "],
            ' ': ["       ", "       ", "       ", "       ", "       ", "       ", "       "]
        }
        
    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None, Color=None, Attr=None, Scale=1):
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_col = col
        for char in self.Text:
            if char in self.glyphs:
                glyph = self.glyphs[char]
            else:
                glyph = ["       "] * 7
                
            for r, line in enumerate(glyph):
                render_line = line
                if self.FillChar:
                    render_line = "".join([self.FillChar if c != " " else " " for c in line])
                    
                if Attr is not None:
                    Mod.write(Panel, row + r, current_col, render_line, attr=Attr)
                else:
                    Mod.write(Panel, row + r, current_col, render_line, color=Color)
                    
            current_col += len(glyph[0]) + 1

class GlitchEffect(BaseEffect):
    def __init__(self, Text, Row=0, Col=0, Speed=20.0, Loop=True, HoldFinal=True, GlitchChance=0.05, clock=time.monotonic):
        super().__init__(Text, Row, Col, Speed, Loop, HoldFinal, False, "", clock)
        self.GlitchChance = GlitchChance
        self.Charset = "!@#$%^&*()_+-=[]{}|;':,./<>?"
        self.rng = random.Random()
        self.seed_offset = random.randint(0, 10000)

    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_cells = set()
        
        if not self.is_active and not (self.is_done and self.HoldFinal):
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        # Use elapsed ticks to seed so the glitch pattern is stable within a tick but changes fast
        ticks = int(self.elapsed * self.Speed)
        self.rng.seed(self.seed_offset + ticks)
        
        if not self.Loop and ticks > len(self.Text) * 2: # arbitrary end point for non-looping glitch
            self.is_done = True
            self.is_active = False

        glitched_text = ""
        for char in self.Text:
            if char != " " and self.rng.random() < self.GlitchChance:
                glitched_text += self.rng.choice(self.Charset)
            else:
                glitched_text += char
                
        for i, char in enumerate(glitched_text):
            current_cells.add((row, col + i))
            
        self.clear_previous_cells(Mod, Panel, current_cells)
        # Randomly color the glitched version
        color = "white"
        if self.rng.random() < self.GlitchChance:
            color = self.rng.choice(["red", "cyan", "magenta", "yellow"])
            
        Mod.write(Panel, row, col, glitched_text, color=color)


class FireEffect(BaseEffect):
    def __init__(self, Row=0, Col=0, Width=10, Height=10, Speed=20.0, clock=time.monotonic):
        super().__init__("", Row, Col, Speed, True, False, False, "", clock)
        self.Width = Width
        self.Height = Height
        self.fire_grid = [[0 for _ in range(Width)] for _ in range(Height)]
        self.chars = [" ", "░", "▒", "▓", "█"]
        self.rng = random.Random()
        self.last_tick = 0
        
    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        h = Height if Height is not None else self.Height
        w = Width if Width is not None else self.Width
        
        if len(self.fire_grid) != h or (h > 0 and len(self.fire_grid[0]) != w):
            self.fire_grid = [[0 for _ in range(w)] for _ in range(h)]
            
        current_cells = set()
        
        if not self.is_active:
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        ticks = int(self.elapsed * self.Speed)
        steps = ticks - self.last_tick
        self.last_tick = ticks
        
        for _ in range(min(steps, 5)):
            if h == 0 or w == 0: break
            for c in range(w):
                if self.rng.random() < 0.35:
                    self.fire_grid[h-1][c] = len(self.chars) - 1
                else:
                    self.fire_grid[h-1][c] = max(0, self.fire_grid[h-1][c] - 2)
                    
            for r in range(h - 2, -1, -1):
                for c in range(w):
                    drift = self.rng.randint(-1, 1)
                    src_c = c + drift
                    if src_c < 0: src_c = 0
                    if src_c >= w: src_c = w - 1
                    
                    src_heat = self.fire_grid[r+1][src_c]
                    decay = self.rng.random() * 0.95
                    
                    self.fire_grid[r][c] = max(0.0, src_heat - decay)

        c_white = getattr(Mod.front, "color_white", 0)
        c_yellow = getattr(Mod.front, "color_yellow", 0)
        c_red = getattr(Mod.front, "color_red", 0)
        
        for r in range(h):
            for c in range(w):
                intensity = int(self.fire_grid[r][c])
                if intensity < 0: intensity = 0
                if intensity >= len(self.chars): intensity = len(self.chars) - 1
                
                if intensity > 0:
                    current_cells.add((row + r, col + c))
                    char = self.chars[intensity]
                    
                    if intensity >= 4:
                        attr = c_white
                    elif intensity >= 2:
                        attr = c_yellow
                    else:
                        attr = c_red
                        
                    Mod.write(Panel, row + r, col + c, char, attr=attr)
                    
        self.clear_previous_cells(Mod, Panel, current_cells)


class SmokeEffect(BaseEffect):
    def __init__(self, Row=0, Col=0, Width=10, Height=10, Speed=15.0, clock=time.monotonic):
        super().__init__("", Row, Col, Speed, True, False, False, "", clock)
        self.Width = Width
        self.Height = Height
        self.grid = [[0.0 for _ in range(Width)] for _ in range(Height)]
        self.chars = [" ", "░", "▒", "▓"]
        self.rng = random.Random()
        self.last_tick = 0
        
    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None):
        self.Update()
        
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        h = Height if Height is not None else self.Height
        w = Width if Width is not None else self.Width
        
        if len(self.grid) != h or (h > 0 and len(self.grid[0]) != w):
            self.grid = [[0.0 for _ in range(w)] for _ in range(h)]
            
        current_cells = set()
        
        if not self.is_active:
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        ticks = int(self.elapsed * self.Speed)
        steps = ticks - self.last_tick
        self.last_tick = ticks
        
        for _ in range(min(steps, 5)):
            if h == 0 or w == 0: break
            
            new_grid = [[0.0 for _ in range(w)] for _ in range(h)]
            
            # Spawn at bottom
            for c in range(w):
                if self.rng.random() < 0.15:
                    new_grid[h-1][c] = 3.99
                else:
                    new_grid[h-1][c] = max(0.0, self.grid[h-1][c] - 0.5)
            
            # Drift and decay upwards
            for r in range(h - 2, -1, -1):
                for c in range(w):
                    drift = self.rng.randint(-2, 2)
                    src_c = c + drift
                    if src_c < 0: src_c = 0
                    if src_c >= w: src_c = w - 1
                    
                    val = self.grid[r+1][src_c]
                    decay = self.rng.random() * 0.25
                    new_grid[r][c] = max(0.0, val - decay)
                    
            self.grid = new_grid

        c_white = getattr(Mod.front, "color_white", 0)
        c_cyan = getattr(Mod.front, "color_cyan", 0)
        c_blue = getattr(Mod.front, "color_blue", 0)
        
        for r in range(h):
            for c in range(w):
                intensity = int(self.grid[r][c])
                if intensity > 0:
                    intensity = min(intensity, 3)
                    current_cells.add((row + r, col + c))
                    char = self.chars[intensity]
                    
                    if intensity == 3:
                        attr = c_white
                    elif intensity == 2:
                        attr = c_cyan
                    else:
                        attr = c_blue
                        
                    Mod.write(Panel, row + r, col + c, char, attr=attr)
                    
        self.clear_previous_cells(Mod, Panel, current_cells)


import math

class SpinText(BaseEffect):
    def __init__(self, Text, Row=0, Col=0, Speed=2.0, FillChar=None, clock=time.monotonic):
        super().__init__(Text, Row, Col, Speed, True, False, False, "", clock)
        self.FillChar = FillChar
        self.glyphs = {
            '0': ["  000  ", " 0   0 ", " 0   0 ", " 0   0 ", " 0   0 ", " 0   0 ", "  000  "],
            '1': ["   1   ", "  11   ", " 1 1   ", "   1   ", "   1   ", "   1   ", " 11111 "],
            '2': ["  222  ", " 2   2 ", "     2 ", "   22  ", "  2    ", " 2     ", " 22222 "],
            '3': ["  333  ", " 3   3 ", "     3 ", "   33  ", "     3 ", " 3   3 ", "  333  "],
            '4': ["    4  ", "   44  ", "  4 4  ", " 4  4  ", " 44444 ", "    4  ", "    4  "],
            '5': [" 55555 ", " 5     ", " 5555  ", "     5 ", "     5 ", " 5   5 ", "  555  "],
            '6': ["  666  ", " 6     ", " 6     ", " 6666  ", " 6   6 ", " 6   6 ", "  666  "],
            '7': [" 77777 ", "     7 ", "    7  ", "   7   ", "  7    ", "  7    ", "  7    "],
            '8': ["  888  ", " 8   8 ", " 8   8 ", "  888  ", " 8   8 ", " 8   8 ", "  888  "],
            '9': ["  999  ", " 9   9 ", " 9   9 ", "  9999 ", "     9 ", "     9 ", "  999  "],
            ':': ["       ", "   .   ", "   .   ", "       ", "   .   ", "   .   ", "       "],
            ' ': ["       ", "       ", "       ", "       ", "       ", "       ", "       "]
        }

    def Render(self, Mod, Panel, Row=None, Col=None, Height=None, Width=None, Color=None, Attr=None):
        self.Update()
        row = Row if Row is not None else self.Row
        col = Col if Col is not None else self.Col
        
        current_cells = set()
        
        if not self.is_active:
            self.clear_previous_cells(Mod, Panel, current_cells)
            return

        theta = self.elapsed * self.Speed
        cos_theta = math.cos(theta)
        is_back = cos_theta < 0
        
        current_col = col
        for char in self.Text:
            if char in self.glyphs:
                glyph = self.glyphs[char]
            else:
                glyph = ["       "] * 7
                
            proj_grid = [[" " for _ in range(7)] for _ in range(7)]
            
            for r in range(7):
                for c in range(7):
                    orig_char = glyph[r][c]
                    if orig_char != " ":
                        new_c = int(3 + (c - 3) * cos_theta)
                        if 0 <= new_c < 7:
                            proj_grid[r][new_c] = self.FillChar if self.FillChar else orig_char
                            
            use_color = Color
            if is_back:
                if Color == "yellow": use_color = "red"
                elif Color == "cyan": use_color = "blue"
                elif Color == "white": use_color = "black"
                elif Color == "green": use_color = "cyan"
            
            for r in range(7):
                for c_idx in range(7):
                    ch = proj_grid[r][c_idx]
                    if ch != " ":
                        current_cells.add((row + r, current_col + c_idx))
                        if Attr is None:
                            Mod.write(Panel, row + r, current_col + c_idx, ch, color=use_color)
                        else:
                            Mod.write(Panel, row + r, current_col + c_idx, ch, attr=Attr)
                        
            current_col += 8
            
        self.clear_previous_cells(Mod, Panel, current_cells)

