# Built in Mods.

If there is more we can express with the basic functionality
of the app, then a mod should be placed here to demonstrate
that ability.

Please Contribute.

[1] about
[2] buttons
[3] fire

[1] about.py (class About)
    This uses the jinja functionality. originally it had used an 
    attached .j2 file, but that felt like bloat.
[2] buttons.py (class Buttons)
    This is the clicking and switching playground. this is still
    growing.
[3] fire.py (class Fire)
    This was a fun project that I created in 2018. this was the 
    first module, and the basis for making some of the functionality
    of the app.
[4] chat.py (class Chat)
    TODO: This ought be a chat server. for any logged user to DM
    any other logged in user and then go into a traditional AOL 
    style messenger.
    This could be invoked python -m deskapp.server chat server | client
    maybe it should be python -m deskapp.mods.chat server | client (this is bad.)
    