import deskapp
from deskapp import TypewriterEffect, PulseEffect, DissolveEffect, MatrixRainEffect, BigText, HugeText, GlitchEffect, SpinText

class EffectsMod(deskapp.Module):
    name = "Effects"
    def __init__(self, app):
        super().__init__(app, self.name)
        self.typewriter = TypewriterEffect("Welcome to Deskapp Effects!", Row=2, Col=2, Speed=10, HoldFinal=True)
        self.pulse = PulseEffect("This is a pulsing text.", Row=4, Col=2, Speed=2.0)
        self.dissolve = DissolveEffect("Press Enter to dissolve this message.", Row=6, Col=2, Speed=5.0)
        self.glitch = GlitchEffect("SYSTEM COMPROMISED", Row=8, Col=2, GlitchChance=0.08)
        self.rain = MatrixRainEffect(Row=1, Col=40, Width=20, Height=12, Speed=20.0)
        self.big = BigText("42", Row=1, Col=65, FillChar="█")
        self.huge = HugeText("42", Row=7, Col=65, FillChar="█")
        self.spin = SpinText("42", Row=15, Col=65, FillChar="█", Speed=2.0)
        
        self.typewriter.Start()
        self.pulse.Start()
        self.rain.Start()
        self.glitch.Start()
        self.spin.Start()

    def page(self, panel):
        self.typewriter.Render(self, panel)
        self.pulse.Render(self, panel)
        self.dissolve.Render(self, panel)
        self.glitch.Render(self, panel)
        self.rain.Render(self, panel)
        self.big.Render(self, panel, Color="cyan")
        self.huge.Render(self, panel, Color="magenta")
        self.spin.Render(self, panel, Color="yellow")

    @deskapp.callback(0, keypress=deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if not self.dissolve.IsActive:
            self.dissolve.Reset()
            self.dissolve.Start()

app = deskapp.App(
    modules=[EffectsMod],
    show_header=False,
    show_footer=False,
    show_messages=False,
    show_menu=False,
    show_box=False,
    show_info_panel=False,
    show_right_panel=False,
    disable_info_panel=True,
    disable_right_panel=True,
    disable_header=True,
    disable_footer=True,
    disable_menu=True,
    disable_messages=True
)
app.start()
