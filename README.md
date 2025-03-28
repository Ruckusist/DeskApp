## | A very Ruckusist Production |

# Deskapp.org

## A console program manager for python apps.

## Install
 `pip install deskapp`

 TODO: find out how to add on the additional modules so that the raspberry pi
 built in stuff can be installed. wifi scanner, bluetooth scanner, deauther.
 yeah, and the android stuff. I havent started in on the level access we have
 on android, but this app works real good in termux.

## Run

`deskapp` from the console will invoke the app. (why? what else should it do here?)
    What kinds of run commands would you want to provide here? Maybe if i had
    a single file app, and i wanted to create an .exe, i could call 
    deskapp build filename.py ... maybe.

    nearly this shouldnt be a thing. questioning the wisdom of a run command
    at all.

## IDEAS FOR GAMES

 - Desklike
 - DeskHunter
 - Desk2042
 - DeskType
 - DeskShip
 - DeskSnake (in progress)
 - DeskFortress

## IDEA FOR APPS

- Linux builder. This seems like a fun challenge. It should have all the
    features of the standing linux config building system, but should offer
    the clickability, and UX of a proper deskapp. You could click this onto
    the deskapp.server and use it for cross-compiling remotely. so a piNano
    deskserver weather station, that is solar powered, could still stay up to
    date because the main system build handles it. good idea.
- Bitcoin Trader (obviously)
- MP3 player / organizer
- RoboDog
- Deskapt: An apt package manager frontend for the terminal.

# IDEAS FOR NEW FUNCTIONALITY
- the string decider should be like the callback system and use
    regular expressions to fire a definded function.

- an inturrupt system/ event system -- cant seem to throw off the
    incoming socket server without crashing it. -- looking for more
    solutions.

## TODO

    [x] Unify the printing mechinism. There are like 3 differe/home/dad/code/DeskApp/examplesnt printing 
        schemes going on in here, and that needs to be fixed. like formost.

    [ ] Freshen up the examples folder; do a new example based on the login
        page where clicking somewhere spawns further pages, and destroys 
        spawned pages.

    [ ] Add in the Web sub-module. see what the viability is of printing
        what we see as deskapp in the terminal to the screen space of a 
        webpage.

    [ ] Use the Pop Up warnings in a demo and see what their viability is.

    [ ] So much... 
        - Shortcuts. Everything in the module needs a functional shortcut. we
            should not be making calls directly to curses, from 3 libraries
            up, that is silly. there has to be a better way to wrap those.

        - Further Mouse support. Mouse handling is now passed to the module, 
            and it is useable. but it is far from clean/good.

        x further draw support. the logic class has draw functions in there. 
            those functions to redraw the screen should either be in the
            frontend class, as an extention, or in a intermediate class that
            can redraw any prebuilt setup of screen.

        x remove all the parts from the screen by toggle.
         x !! Also i want to be able to start with the visibility of everything
            turned off. so the module is full screen.
            [x] Toggle Menu.
            [x] Toggle Header.
            [x] Toggle Meta.
            [x] Toggle Footer.
            [x] Toggle Messages.
        
        x Fullsceen messages, full screen module page.

    [ ] Reproduce all this work in other programming languages. I have heard a 
        legend of a javascript module that if you write the code out in their
        style, then it can just output many different languages from one template.
        this would be a cool exercise. its fun to think that this might be a 
        cooler idea outside the python community than within it.

    [ ] Stream all this work on twitch. Then clip that into coherient tutorials
        for youtube. your gonna do the work anyway, record it.

## SUB MODULES

Sub Projects have been moved into this namespace. This might be a bad idea in the
long run. But for the short term, having all the moving parts in one project 
directory is a boon.

    - THE SERVER.
        The Server is a python socket server. With a login database, Messaging
            protocol for arbitary file sizes, Compression/Encryption, a message passing
            protocol for multiplayer apps, like a chat server.

    - WEB SERVER.
        The Web Server should come with a javascript library that can connect
            to 'The Server'. and a login page, start with some ping-pong after that.

## KNOWN BUGS
11.3.23 - Starting a blank app with only demo mode turned off, will result in no mods being loaded and the decider cant load available panels.

## ChangeLog
6.10.23-Ruckusist: Starting to reassamble the onefile back into a One.0 version.
3.11.23-Ruckusist: Deskapp.org - is now a thing.
3.11.23-Lannocc v0.0.12: Live terminal resizing now works!

3.11.23-Lannocc v0.0.11: Actually fixed the sizing problem this time.

3.11.23-Ruckusist v0.0.10: I have a stable enough onefile, im going to start
    a twofile. Onefile should accept no more feature upgrade, and just get
    the final bug fixes in before it migrates to a mutlifile for the 1.0 
    release. much left to do.

3.5.23-Lannocc v0.0.9: Fixed a sizing anomaly.

11.11.22-Ruckusist v.0.0.8: Added in the Server. The server has a long todo list please check this out if you want to help.

11.11.22-Ruckusist v.0.0.7: Added in mouse support. Refactored some parts in 
    previous 4-6 updates. No changes to the working API

7.26.22-Ruckusist v.0.0.4: release of version 4. This version come with new, and
    significant bugs, But with new functionality. This is just a transition point
    from one stable/working version, to the next.

4.20.22-Ruckusist v0.0.4: started working version 4.

4.6.22-Ruckusist v0.0.3: added the demo_mode flag to the App Object to turn off
    the About and Fire functionality. This gives me the idea to put more demo 
    stuff there. I want to copy cmatrix, dropping snowflakes, video player, other 
    stuff.
