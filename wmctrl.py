import os
import subprocess
from collections import namedtuple
import re

#This code is heavily inspired by a wmctrl module by Antonio Cuni: bitbucket.org/antocuni/wmctrl
# His module does a ton of stuff I don't care about though, so I've built mine from scratch.
BaseWindow = namedtuple('Window', ['id', 'desktop', 'pid', 'x', 'y', 'w', 'h', 'wm_class', 'host', 'wm_name'])

class Window(BaseWindow):
	@classmethod
	def list(cls):
		"""Returns a list of Window objects, one for each window open."""
		out = subprocess.check_output(['wmctrl','-l','-G','-p','-x'])
		windows = []
		for line in out.splitlines():
			parts = line.split(None, len(cls._fields)-1)
			parts = [p.strip() for p in parts]
			parts[1:7] = [int(p) for p in parts[1:7]]
			if len(parts) == 9: #Title field is missing
				parts.append('')
			windows.append(cls(*parts))
		return windows

	@classmethod
	def by_name(cls, pattern, on_current_desktop=False):
		"""Returns all windows matching 'pattern'."""
		wins = [win for win in cls.list() if re.match(pattern, win.wm_name) is not None]
		if on_current_desktop:
			wins = [win for win in wins if win.desktop == current_desktop()]
		return wins
	
	def activate(self):
		"""Activate (bring to front and give focus to) the window."""
		if not (self.id in [w.id for w in self.list()]):
			raise Exception("Attemped to activate non-existant window.")
		subprocess.call(['wmctrl', '-id', '-a', self.id])

	def move_to_current_desktop_and_activate(self):
		"""Move the window to the current desktop, then activate it."""
		subprocess.call(['wmctrl', '-id', '-R', self.id])

def current_desktop():
	out = subprocess.check_output(['wmctrl', '-d'])
	for line in out.splitlines():
		parts = line.split()
		if parts[1] == "*":
			return int(parts[0])
	# if you get this far, something has gone horribly wrong.
	raise ValueError("Unable to determine current desktop from wmctrl output.")

def _wm_switch_to_desktop(desktop_id):
	subprocess.call(['wmctrl', '-s', str(desktop_id)])
