# The MIT License
#
# Copyright (c) 2014 Vu Nhat Minh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import curses
import heapq
import itertools
from functools import wraps
from pyfiglet import figlet_format

# Global variable
description = {
  "switch ": "Switch stream. You can use either 'switch public' or 'switch mine'",
  "home "  : "Show your timeline. 'home 7' will show 7 tweet.",
  "view "  : "'view @mdo' will show @mdo's home.",
  "h "     : "Show help.",
  "t "     : "'t opps' will tweet 'opps' immediately.",
  "s "     : "'s #AKB48' will search for '#AKB48' and return 5 newest tweets."
}
g = {}
buf = {}
screen = None
enter_ary = [curses.KEY_ENTER,10]
delete_ary = [curses.KEY_BACKSPACE,curses.KEY_DC,8,127,263]
tab_ary = [9]
up_ary = [curses.KEY_UP]
down_ary = [curses.KEY_DOWN]

# Init curses screen
screen = curses.initscr()
screen.keypad(1)
curses.noecho()
try:
  curses.start_color()
  curses.use_default_colors()
  for i in range(0, curses.COLORS):
    curses.init_pair(i + 1, i, -1)
except curses.error:
  pass
curses.cbreak()
g['height'] , g['width'] = screen.getmaxyx()

# Init color function
white = lambda x:curses_print_word(x,0)
grey = lambda x:curses_print_word(x,1)
red = lambda x:curses_print_word(x,2)
green = lambda x:curses_print_word(x,3)
yellow = lambda x:curses_print_word(x,4)
blue = lambda x:curses_print_word(x,5)
magenta = lambda x:curses_print_word(x,6)
cyan = lambda x:curses_print_word(x,7)
colors_shuffle = [grey, red, green, yellow, blue, magenta, cyan]
cyc = itertools.cycle(colors_shuffle[1:])
index_cyc = itertools.cycle(range(1,8))


def Memoize(func):
    """
    Memoize decorator
    """
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


@Memoize
def cycle_color(s):
    """
    Cycle the colors_shuffle
    """
    return next(cyc)


def ascii_art(text):
    """
    Draw the Ascii Art
    """
    fi = figlet_format(text, font='doom')
    for i in fi.split('\n'):
      curses_print_line(i,next(index_cyc))


def close_window():
  """
  Close screen
  """
  global screen
  screen.keypad(0);
  curses.nocbreak();
  curses.echo()
  curses.endwin()


def suggest(word):
  """
  Find suggestion
  """
  rel = []
  if not word: return rel
  for candidate in description:
    if candidate.startswith(word):
      rel.append(candidate)
  return rel


def curses_print_word(word,color_pair_code):
  """
  Print a word
  """
  word = word.encode('utf8')
  screen.addstr(word,curses.color_pair(color_pair_code))


def curses_print_line(line,color_pair_code):
  """
  Print a line, scroll down if need
  """
  line = line.encode('utf8')
  y,x = screen.getyx()
  if y - g['height'] == -3:
    scroll_down(2,y,x)
    screen.addstr(y,0,line,curses.color_pair(color_pair_code))
    buf[y] = line, color_pair_code
  elif y - g['height'] == -2:
    scroll_down(3,y,x)
    screen.addstr(y-1,0,line,curses.color_pair(color_pair_code))
    buf[y-1] = line ,color_pair_code
  else:
    screen.addstr(y+1,0,line,curses.color_pair(color_pair_code))
    buf[y+1] = line, color_pair_code


def redraw(start_y,end_y,fallback_y,fallback_x):
  """
  Redraw lines from buf
  """
  for cursor in range(start_y,end_y):
    screen.move(cursor,0)
    screen.clrtoeol()
    try:
      line, color_pair_code = buf[cursor]
      screen.addstr(cursor,0,line,curses.color_pair(color_pair_code))
    except:
      pass
  screen.move(fallback_y,fallback_x)


def scroll_down(noredraw,fallback_y,fallback_x):
  """
  Scroll down 1 line
  """
  # Recreate buf
  # noredraw = n means that screen will scroll down n-1 line
  trip_list = heapq.nlargest(noredraw-1,buf)
  for i in buf:
    if i not in trip_list:
      buf[i] = buf[i+noredraw-1]
  for j in trip_list:
    buf.pop(j)

  # Clear and redraw
  screen.clear()
  redraw(1,g['height']-noredraw,fallback_y,fallback_x)


def clear_upside(n,y,x):
  """
  Clear n lines upside
  """
  for i in range(1,n+1):
    screen.move(y-i,0)
    screen.clrtoeol()
  screen.refresh()
  screen.move(y,x)


def display_suggest(y,x,word):
  """
  Display box of suggestion
  """
  side = 2

  # Check if need to print upside
  upside = y+6 > int(g['height'])

  # Redraw if suggestion is not the same as previous display
  sug = suggest(word)
  if sug != g['prev']:
    # 0-line means there is no suggetions (height = 0)
    # 3-line means there are many suggetions (height = 3)
    # 5-line means there is only one suggetions (height = 5)
    # Clear upside section
    if upside:
      # Clear upside is a bit difficult. Here it's seperate to 4 case.
      # now: 3-lines / previous : 0 line
      if len(sug) > 1 and not g['prev']:
        clear_upside(3,y,x)
      # now: 0-lines / previous :3 lines
      elif not sug and len(g['prev'])>1:
        redraw(y-3,y,y,x)
      # now: 3-lines / previous :5 lines
      elif len(sug) > 1 == len(g['prev']):
        redraw(y-5,y-3,y,x)
        clear_upside(3,y,x)
      # now: 5-lines / previous :3 lines
      elif len(sug) == 1 < len(g['prev']):
        clear_upside(3,y,x)
      # now: 0-lines / previous :5 lines
      elif not sug and len(g['prev'])==1:
        redraw(y-5,y,y,x)
      # now: 3-lines / previous :3 lines
      elif len(sug) == len(g['prev']) > 1:
        clear_upside(3,y,x)
      # now: 5-lines / previous :5 lines
      elif len(sug) == len(g['prev']) == 1:
        clear_upside(5,y,x)
      screen.refresh()
    else:
    # Clear downside
      screen.clrtobot()
      screen.refresh()
  g['prev'] = sug

  if sug:
    # More than 1 suggestion
    if len(sug) > 1:
      needed_lenth = sum([len(i)+side for i in sug]) + side
      if upside:
        win = curses.newwin(3,needed_lenth,y-3,0)
        win.erase()
        win.box()
        win.refresh()
        cur_width = side
        for i in range(len(sug)):
          screen.addstr(y-2,cur_width,sug[i],curses.color_pair(4))
          cur_width += len(sug[i]) + side
      else:
        win = curses.newwin(3,needed_lenth,y+1,0)
        win.erase()
        win.box()
        win.refresh()
        cur_width = side
        for i in range(len(sug)):
          screen.addstr(y+2,cur_width,sug[i],curses.color_pair(4))
          cur_width += len(sug[i]) + side
    # Only 1 suggestion
    else:
      can = sug[0]
      if upside:
        win = curses.newwin(5,len(description[can])+2*side,y-5,0)
        win.box()
        win.refresh()
        screen.addstr(y-4,side,can,curses.color_pair(4))
        screen.addstr(y-2,side,description[can],curses.color_pair(3))
      else:
        win = curses.newwin(5,len(description[can])+2*side,y+1,0)
        win.box()
        win.refresh()
        screen.addstr(y+2,side,can,curses.color_pair(4))
        screen.addstr(y+4,side,description[can],curses.color_pair(3))


def inputloop():
  """
  Main loop input
  """
  word = ''
  g['prev'] = None
  g['tab_cycle'] = None
  g['prefix'] = '[@dtvd88]: '
  g['hist_index'] = 0
  # Load history from previous session
  try:
    o = open('completer.hist')
    g['hist'] = [i.strip() for i in o.readlines()]
  except:
    g['hist'] = []

  screen.addstr("\n" + g['prefix'],curses.color_pair(240))

  while True:
    # Current position
    y,x = screen.getyx()
    # Get char
    event = screen.getch()
    try :
      char = chr(event)
    except:
      char = ''

    # Test curses_print_line
    if char == '?':
      buf[y] = g['prefix'] + '?', 0
      ascii_art('dtvd88')

    # TAB to complete
    elif event in tab_ary:
      # First tab
      try:
        if not g['tab_cycle']:
          g['tab_cycle'] = itertools.cycle(suggest(word))

        suggestion = next(g['tab_cycle'])
        # Clear current line
        screen.move(y,len(g['prefix']))
        screen.clrtoeol()
        # Print out suggestion
        word = suggestion
        screen.addstr(y,len(g['prefix']),word)
        display_suggest(y,x,word)
        screen.move(y,len(word)+len(g['prefix']))
      except:
        pass

    # UP key
    elif event in up_ary:
      if g['hist']:
        # Clear current line
        screen.move(y,len(g['prefix']))
        screen.clrtoeol()
        # Print out previous history
        if g['hist_index'] > 0 - len(g['hist']):
          g['hist_index'] -= 1
        word = g['hist'][g['hist_index']]
        screen.addstr(y,len(g['prefix']),word)
        display_suggest(y,x,word)
        screen.move(y,len(word)+len(g['prefix']))

    # DOWN key
    elif event in down_ary:
      if g['hist']:
        # clear current line
        screen.move(y,len(g['prefix']))
        screen.clrtoeol()
        # print out previous history
        if not g['hist_index']:
          g['hist_index'] = -1
        if g['hist_index'] < -1:
          g['hist_index'] += 1
        word = g['hist'][g['hist_index']]
        screen.addstr(y,len(g['prefix']),word)
        display_suggest(y,x,word)
        screen.move(y,len(word)+len(g['prefix']))

    # Enter key
    elif event in enter_ary:
      g['tab_cycle'] = None
      g['hist_index'] = 0
      g['hist'].append(word)
      if word== 'q':
        o = open('completer.hist','w')
        o.write("\n".join(g['hist']))
        o.close()
        break;
      display_suggest(y,x,'')
      screen.clrtobot()
      buf[y] = g['prefix'] + word, 0
      # Touch the screen's end
      if y - g['height'] > -3:
        scroll_down(2,y,x)
        screen.addstr(y,0,g['prefix'],curses.color_pair(240))
      else:
        screen.addstr(y+1,0,g['prefix'],curses.color_pair(240))
      word = ''

    # Delete / Backspace
    elif event in delete_ary:
      g['tab_cycle'] = None
      # Touch to line start
      if x < len(g['prefix']) + 1:
        screen.move(y,x)
        word = ''
      # Midle of line
      else:
        word = word[:-1]
        screen.move(y,x-1)
        screen.clrtoeol()
        display_suggest(y,x,word)
        screen.move(y,x-1)

    # Another keys
    else:
      g['tab_cycle'] = None
    # Explicitly print char
      screen.addstr(char)
      word += char
      display_suggest(y,x,word)
      screen.move(y,x+1)

  # Reset
  close_window()


if __name__ == "__main__":
  inputloop()