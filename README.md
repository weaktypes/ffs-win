# ffs-win
Switch to Quake window when the specific map is currently played or comes next in the FFA mapcycle.

## Description

This script can come handy if you're on a FFA server with many maps in rotation but you only want to play some of them. Instead of waiting for your preferred map to come up, you can run this script and it will automatically bring the Quake window to the forefront.

You can specify the maps that will trigger the switch if they're currently played.

If the map rotation is sequential and not random, you can also set the maps that precede your preferred maps and the window will be brought to the forefront during the standby screen so you don't miss the start of the match.

There's also an option to auto-join.

## Compatibility

This is a Windows-only script that works with ezQuake. It may work with other clients as long as their window title is in "normal - x/x - mapname" and "standby - x/x - mapname" format. Tested on Windows 10 and ezQuake 3.6 with USB and PS/2 keyboards.

## Usage

`python ffs.py [options]`

`ffs.exe [options]`

| option        | functionality |
| :--- | :--- |
| `-h`, `--help`      | show the help screen |
| `-p`,&nbsp;`--preceding`      | list of the maps that precede the maps that you want to play - after Quake client reaches standby screen after one of these maps, switch is made; can be combined with `--wanted` (separated with commas or spaces)      |
| `-w`, `--wanted`      | list of maps that you want to play - switches to Quake client if one of these maps is played; can be combined with `--preceding` (separated with commas or spaces)      |
| `-j`, `--join`      | send keys to join the game automatically (see note below)      |
| `-n`, `--next`      | switch to Quake window on the next standby screen      |
| `-e`, `--noexit`      | don't exit after switching      |
| `-i`, `--interval`      | how often the window titles are checked, in seconds (you can set this to value like 0.5 if you feel that the default 1 is too high)      |

### Examples

Switches to Quake window after ztndm6, panzer or rapture1 is finished, then exits:

`ffs.exe -p ztndm6,panzer,rapture1`

`ffs.exe -p "ztndm6 panzer rapture1"`

Switches to Quake window if efdm8 or ultrav is currently played, keeps switching
until it's closed:

`ffs.exe -w efdm8,ultrav -e`

Switches to Quake window on the next standby screen, joins the game, then exits:

`ffs.exe -n -j`

Switches to Quake window on every standby screen:

`ffs.exe -n -e`

### Notes
 
--join function sends a sequence of keys that opens the console, writes /join,
presses Enter and closes the console. For this to work, Quake must be in a state where
this sequence has a desired effect (i.e. with no console and no in-game menu open).

To prevent the situation where the program would keep switching to Quake window when you
try to alt-tab from it (when --noexit parameter is used), a switch is only made once
during the match and once during the standby (then another might be done when the next
match starts or the next stanby is reached).

## Known issues

For some reason, ezQuake 3.6 freezes for a few seconds after a new map is started. During those few seconds, the title of the window is "standby - x/x - " and the name of the new map, which may trigger the switch before, not after the map is played (if the `--preceding` option is used). Will I try to do something about it? I don't know.
