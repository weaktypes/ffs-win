import ctypes
import time
import sys
import getopt
import re
import datetime

def join_game():
	for scancode in [0xC0, 0x6F, 0x4A, 0x4F, 0x49, 0x4E, 0x0D, 0xC0]:
		ctypes.WinDLL('user32').keybd_event(scancode, ctypes.WinDLL('user32').MapVirtualKeyW(scancode, 0), 0, 0)
		ctypes.WinDLL('user32').keybd_event(scancode, ctypes.WinDLL('user32').MapVirtualKeyW(scancode, 0), 0x0002, 0)
		time.sleep(0.1)

def find_window_by_title(start_string):
	window_handle = ctypes.WinDLL('user32').FindWindowW(None, None)
	
	while window_handle:
		title = ctypes.create_unicode_buffer(1024)
		ctypes.WinDLL('user32').GetWindowTextW(window_handle, title, 1024)
		if title.value.startswith(start_string):
			return (window_handle, title.value)
		window_handle = ctypes.WinDLL('user32').FindWindowExW(None, window_handle, None, None)
	
	return None

def time_now():
	return datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

def main():

	# default settings
	wanted_maps = []
	preceding_maps = []
	exit_after_switch = True
	switch_before_next = False
	do_join = False
	check_interval = 1

	help1 = """
 > Usage:

 ffs.exe [options]
 
 -h, --help		show this help screen
 -e, --noexit 		don't exit after switching to Quake window
 -n, --next		switch to Quake window on the next mapchange
 -j, --join		send keys to join the game automatically (see note below)
 -p, --preceding	list of the maps that precede the maps that you want to play -
 			after Quake client reaches standby screen after one of these maps,
 			switch is made (separated with commas or spaces)
 -w, --wanted		list of maps that you want to play - switches to Quake client
 			if one of these maps is played (separated with commas or spaces)
 -i, --interval 	how often the window titles are checked, in seconds (you can set 
 			this to value like 0.5 if you feel that the default 1 is too high)

 > Notes:
 
 --join function sends a sequence of keys that opens the console, writes /join,
 presses Enter and closes the console. For this to work, Quake must be in a state where
 this sequence has a desired effect (i.e. with no console and no in-game menu open).

 To prevent the situation where the program would keep switching to Quake window when you
 try to alt-tab from it (when --noexit parameter is used), a switch is only made once
 during the match and once during the standby (then another might be done when the next
 match starts or the next stanby is reached).
 
 > Examples:
 
 Switches to Quake window after ztndm6, panzer or rapture1 is finished, then exits:
 
 ffs.exe -p ztndm6,panzer,rapture1
 ffs.exe -p "ztndm6 panzer rapture1"
 
 Switches to Quake window if efdm8 or ultrav is currently played, keeps switching
 until it's closed:
 
 ffs.exe -w efdm8,ultrav -e
 
 Switches to Quake window on the next standby screen, joins the game, then exits:
 
 ffs.exe -n -j
 
 Switches to Quake window on every standby screen:
 
 ffs.exe -n -e
"""

	if len(sys.argv) > 1:
		try:
			opts, args = getopt.getopt(sys.argv[1:], "henjp:w:i:", ["help", "noexit", "next", "join", "preceding=", "wanted=", "interval="])
		except getopt.GetoptError as e:
			print(e)
			sys.exit(help1)

		mapname_regex = re.compile(r'^[a-z0-9-_]+$')

		for opt, arg in opts:
			if opt in ("-h", "--help"):
				sys.exit(help1)

			if opt in ("-e", "--noexit"):
				exit_after_switch = False

			if opt in ("-n", "--next"):
				switch_before_next = True

			if opt in ("-j", "--join"):
				do_join = True

			if opt in ("-p", "--preceding"):
				if " " in arg:
					preceding_maps = arg.split(" ")
				elif "," in arg:
					preceding_maps = arg.split(",")
				else:
					preceding_maps = [arg]
				preceding_maps = [i for i in preceding_maps if mapname_regex.match(i)]

			if opt in ("-w", "--wanted"):
				if " " in arg:
					wanted_maps = arg.split(" ")
				elif "," in arg:
					wanted_maps = arg.split(",")
				else:
					wanted_maps = [arg]
				wanted_maps = [i for i in wanted_maps if mapname_regex.match(i)]

			if opt in ("-i", "--interval"):
				if re.match(r"^[0-9](\.[0-9]{1,10})?$", arg):
					check_interval = float(arg)
					if check_interval < 0.1:
						check_interval = 0.1
				else:
					exit("\nError: Invalid value used to set interval")

	if len(wanted_maps) == 0 and len(preceding_maps) == 0 and switch_before_next is False:
		sys.exit("\nError: No preceding or wanted maps set, no switch-on-next option selected")

	do_preceding = True if len(preceding_maps) > 0 else False
	do_wanted = True if len(wanted_maps) > 0 else False
	dont_switch_to = False
	dont_switch_standby = False

	print("")

	while True:

		if do_preceding or switch_before_next or dont_switch_to:
			handle_title = find_window_by_title("standby - ")

			if handle_title is not None:

				if dont_switch_to:
					print(f"[{time_now()}] OK to switch to {dont_switch_to} now")
					dont_switch_to = False

				handle, title = handle_title

				if switch_before_next and not dont_switch_standby:

					handle_active_window = ctypes.WinDLL('user32').GetForegroundWindow()
					if handle_active_window == handle:
						print(f"[{time_now()}] Quake window already in the foreground")
						dont_switch_standby = True
						continue

					print(f"[{time_now()}] Switching to process {handle}, title: {title}")
					ctypes.WinDLL('user32').SwitchToThisWindow(handle, True)
					if do_join:
						time.sleep(0.3)
						join_game()
					if exit_after_switch:
						sys.exit()
					else:
						dont_switch_standby = True

				elif do_preceding and not dont_switch_standby:
					mapname = title[title.rfind(" ")+1:]
					if mapname in preceding_maps:

						handle_active_window = ctypes.WinDLL('user32').GetForegroundWindow()
						if handle_active_window == handle:
							print(f"[{time_now()}] Quake window already in the foreground")
							dont_switch_standby = True
							continue

						print(f"[{time_now()}] Switching to process {handle}, title: {title}")
						ctypes.WinDLL('user32').SwitchToThisWindow(handle, True)
						if do_join:
							time.sleep(0.3)
							join_game()
						if exit_after_switch:
							sys.exit()
						else:
							dont_switch_standby = True

		if do_wanted or dont_switch_standby:
			handle_title = find_window_by_title("normal - ")

			if handle_title is not None:

				if dont_switch_standby:
					dont_switch_standby = False

				if do_wanted:

					handle, title = handle_title
					mapname = title[title.rfind(" ")+1:]

					if mapname in wanted_maps and mapname != dont_switch_to:

						handle_active_window = ctypes.WinDLL('user32').GetForegroundWindow()
						if handle_active_window == handle:
							print(f"[{time_now()}] Quake window already in the foreground")
							dont_switch_to = mapname
							print(f"[{time_now()}] No switching to {mapname} until next standby")
							continue

						print(f"[{time_now()}] Switching to process {handle}, title: {title}")
						ctypes.WinDLL('user32').SwitchToThisWindow(handle, True)
						if do_join:
							time.sleep(0.3)
							join_game()
						if exit_after_switch:
							sys.exit()
						else:
							dont_switch_to = mapname
							print(f"[{time_now()}] No switching to {mapname} until next standby")

		time.sleep(check_interval)

if __name__ == "__main__":
	main()
