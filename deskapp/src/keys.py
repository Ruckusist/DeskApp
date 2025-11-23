"""
Deskapp 1.0
app.py
last updated: 6-10-23
updated by: Ruckusist
State: Good. Stable.
"""

import enum

class Keys(enum.IntEnum):
    """Remap the keypresses from numbers to variables."""
    UP    = 259
    DOWN  = 258
    LEFT  = 260
    RIGHT = 261
    ENTER = 10
    SPACE = 32
    BACKSPACE = 263
    HOME  = 262
    END   = 360
    ESC   = 27
    Q = 113
    q = 81
    W = 119
    E = 101
    R = 114
    T = 116
    Y = 121
    U = 117
    I = 105
    O = 111
    P = 112
    A = 97
    a = 97
    S = 115
    s = 115
    D = 100
    d = 100
    F = 102
    f = 102
    G = 103
    g = 103
    H = 104
    h = 104
    J = 106
    j = 106
    K = 107
    k = 107
    L = 108
    l = 108
    Z = 122
    z = 122
    X = 120
    x = 120
    C = 99
    c = 99
    V = 118
    v = 118
    B = 98
    b = 98
    N = 110
    n = 110
    M = 109
    m = 109

    #

    # F KEYS
    F1    = 80

    # NUMBER KEYS
    NUM1   = 49
    NUM2   = 50
    NUM3   = 51
    NUM4   = 52
    NUM5   = 53
    NUM6 = 54
    NUM7 = 55
    NUM8 = 56
    NUM9 = 57
    NUM0 = 48

    # DEFAULT KEYS
    TAB     = 9
    PG_DOWN = 338
    PG_UP   = 339

    # MOUSE CLICKS
    LEFT_CLICK_DOWN = 2
    LEFT_CLICK_UP = 1
    RIGHT_CLICK_DOWN = 2048
    RIGHT_CLICK_UP = 1024
    MIDDLE_CLICK_DOWN = 64
    MIDDLE_CLICK_UP = 32

    # SIGNALS
    RESIZE = 410
    FOCUS = 589
    LOST_FOCUS = 588