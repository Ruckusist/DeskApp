try:
    import deskapp
except ImportError:
    print("#==? [ERR] You must install Deskapp first.")
    print("#==> [COPY] pip install -U deskapp")
    print("#--> Then Try again. See Ruckusist.com for more info.")
    exit(1)
app = deskapp.App()
app.start()