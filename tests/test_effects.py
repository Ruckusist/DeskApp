import pytest
import time
from deskapp.src.effects import (
    BaseEffect,
    TypewriterEffect,
    PulseEffect,
    DissolveEffect,
    MatrixRainEffect,
    BigText,
    ColorPalette
)

class MockFront:
    def __init__(self):
        self.color_white = 1
        self.color_green = 2
        self.palette = [0, 1, 2, 3, 4]
        self.output = []
        
    def safe_addstr(self, win, row, col, string, attr):
        self.output.append((row, col, string, attr))

class MockApp:
    def __init__(self):
        self.front = MockFront()

class MockPanel:
    def __init__(self):
        self.win = "win"
        self.dims = [20, 20]

class MockMod:
    def __init__(self):
        self.front = MockFront()
        self.written = []
    
    def write(self, panel, row, col, string, color=None, attr=None):
        c = attr if attr is not None else color
        self.written.append((row, col, string, c))
        return True

def test_base_effect_timing():
    # Use a predictable clock
    times = [0.0, 0.5, 1.0]
    def mock_clock():
        return times.pop(0)
        
    effect = BaseEffect("Test", clock=mock_clock)
    effect.Start()
    
    assert effect.IsActive
    effect.Update() # elapsed = 0.5
    assert effect.elapsed == 0.5
    
def test_typewriter():
    times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    def mock_clock(): return times.pop(0)
    
    effect = TypewriterEffect("ABC", Speed=10.0, clock=mock_clock, ShowCursor=False)
    effect.Start()
    mod = MockMod()
    panel = MockPanel()
    
    # 0.1s * 10 = 1 char
    effect.Render(mod, panel)
    assert mod.written[-1][2] == "A"
    
    # 0.2s * 10 = 2 chars
    mod.written.clear()
    effect.Render(mod, panel)
    assert mod.written[-1][2] == "AB"
    
    # 0.3s * 10 = 3 chars
    mod.written.clear()
    effect.Render(mod, panel)
    assert mod.written[-1][2] == "ABC"
    assert effect.IsDone
    assert not effect.IsActive

def test_pulse_effect():
    times = [0.0, 0.5, 1.0, 1.5]
    def mock_clock(): return times.pop(0)
    
    effect = PulseEffect("Test", Speed=2.0, Loop=True, Colors=["red", "blue"], clock=mock_clock)
    effect.Start()
    mod = MockMod()
    panel = MockPanel()
    
    # 0.5s * 2 = index 1
    effect.Render(mod, panel)
    assert mod.written[-1][3] == "blue"
    
    # 1.0s * 2 = index 2 % 2 = 0
    effect.Render(mod, panel)
    assert mod.written[-1][3] == "red"

def test_dissolve_effect():
    times = [0.0, 0.2, 0.4, 0.6, 0.8]
    def mock_clock(): return times.pop(0)
    
    effect = DissolveEffect("Test", Speed=5.0, Charset=["*"], Seed=42, clock=mock_clock)
    effect.Start()
    mod = MockMod()
    panel = MockPanel()
    
    # 0.2s * 5 = stage 1
    effect.Render(mod, panel)
    out1 = mod.written[-1][2]
    assert len(out1) == 4
    
    # 0.4s * 5 = stage 2
    effect.Render(mod, panel)
    out2 = mod.written[-1][2]
    # At stage 2, more chars should be dissolved (they become spaces eventually)
    
def test_bigtext():
    mod = MockMod()
    panel = MockPanel()
    bt = BigText("1")
    bt.Render(mod, panel, Row=0, Col=0)
    
    # '1' has 5 rows
    assert len(mod.written) == 5
    assert mod.written[0][2] == "  1  "

def test_matrix_rain_reproducibility():
    times = [0.0, 0.5]
    def mock_clock(): return times.pop(0)
    
    effect1 = MatrixRainEffect(Width=2, Height=5, Speed=10.0, Seed=123, clock=mock_clock)
    effect1.Start()
    
    mod = MockMod()
    panel = MockPanel()
    
    effect1.Render(mod, panel)
    out1 = list(mod.written)
    mod.written.clear()
    
    times2 = [0.0, 0.5]
    def mock_clock2(): return times2.pop(0)
    
    effect2 = MatrixRainEffect(Width=2, Height=5, Speed=10.0, Seed=123, clock=mock_clock2)
    effect2.Start()
    effect2.Render(mod, panel)
    out2 = list(mod.written)
    
    # Because of the seed and same time elapsed, outputs should be exactly the same
    assert len(out1) == len(out2)
    for a, b in zip(out1, out2):
        assert a == b

