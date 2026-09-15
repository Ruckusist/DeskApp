import time
import deskapp
from deskapp import MatrixRainEffect, FireEffect, SmokeEffect, SpinText

class ClockMod(deskapp.Module):
    name = "Clock"
    def __init__(self, app):
        super().__init__(app, self.name)
        self.rain = MatrixRainEffect(Row=0, Col=0, Width=80, Height=24, Speed=15.0)
        self.fire = FireEffect(Row=0, Col=0, Width=80, Height=24, Speed=15.0)
        self.smoke = SmokeEffect(Row=0, Col=0, Width=80, Height=24, Speed=12.0)
        
        self.rain.Start()
        self.fire.Start()
        self.smoke.Start()
        
        self.active_effect = 0 # 0=rain, 1=fire, 2=smoke
        
        self.spin_text = SpinText("", FillChar="█", Speed=2.0)
        self.spin_text.Start()

    def page(self, panel):
        t_str = time.strftime("%H:%M:%S")
        self.spin_text.Text = t_str
        
        try:
            ph, pw = int(panel.dims[0]), int(panel.dims[1])
        except Exception:
            ph, pw = self.h, self.w
            
        self.rain.Width = pw
        self.rain.Height = ph
        self.fire.Width = pw
        self.fire.Height = ph
        self.smoke.Width = pw
        self.smoke.Height = ph
            
        if self.active_effect == 0:
            self.rain.Render(self, panel, Row=0, Col=0)
            self.fire.is_active = False
            self.smoke.is_active = False
            if not self.rain.is_active: self.rain.Start()
        elif self.active_effect == 1:
            self.fire.Render(self, panel, Row=0, Col=0)
            self.rain.is_active = False
            self.smoke.is_active = False
            if not self.fire.is_active: self.fire.Start()
        else:
            self.smoke.Render(self, panel, Row=0, Col=0)
            self.rain.is_active = False
            self.fire.is_active = False
            if not self.smoke.is_active: self.smoke.Start()
        
        # 8 chars ("HH:MM:SS") * 8 = 64 width
        start_col = max(0, (pw - 64) // 2)
        start_row = max(0, (ph - 7) // 2)
        
        self.spin_text.Render(self, panel, Row=start_row, Col=start_col, Color="yellow")
        
        # Help text
        self.write(panel, ph - 1, 1, "[SPACE] Toggle Background  [Q] Quit", color="white")

    @deskapp.callback(0, keypress=deskapp.Keys.SPACE)
    def on_space(self, *args, **kwargs):
        self.active_effect = (self.active_effect + 1) % 3
        # Trigger an immediate screen clear so artifacts don't persist during the switch
        self.app.front.screen.clear()

app = deskapp.App(
    modules=[ClockMod], 
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
