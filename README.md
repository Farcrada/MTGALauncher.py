# MTGALauncher.py
Since the original `MTGALauncher.exe` doesn't work on Linux without significant botching, I translated it to python. Instead of windows calls it'll make calls to your `WINEPREFIX` where `MTGA` is installed.

# WARNING!
This is pretty much untested, this might fuck your `MTGA`-install (`WINEPREFIX` maybe? But might aswell delete the prefix if `MTGA`-install is fucked, no?), so make sure you have a back-up (Just duplicate your prefix folder). I doubt we'll be needing this, but nonetheless: I'd love to hear about it, even if it went successfully.

Make sure your `MTGA.exe` tells you your game is out of date and you /NEED/ to run `MTGLauncher.exe`, otherwise this'll just be a waste of time (You see this /AFTER/ logging in and trying to actually get into the game.).

# Use
Once again! Make sure your `MTGA.exe` tells you your game is out of date and you /NEED/ to run `MTGLauncher.exe`, otherwise this'll just be a waste of time (You see this /AFTER/ logging in and trying to actually get into the game.).

Place the `MTGALauncher.py` next to the `MTGA.exe` and execute it in a terminal (`./MTGALauncher.py`)

Wait for it to finish (it'll launch `MTGA.exe` for you) and see if `MTGA.exe` will now let you log in. Please do report any issues you have as it'll undoubtedly help the cause.
