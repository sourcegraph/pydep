import os
import shutil
import stat
import sys


def rmtree(dir):
	"""
	Recursivly removes files in a given dir. 
	On Windows tries to remove readonly files (i.e. contents of .git)
	"""
	if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'msys':
		shutil.rmtree(dir, onerror =__fix_read_only)
	else:
		shutil.rmtree(dir)

def __fix_read_only(fn, path, excinfo):
	os.chmod(path, stat.S_IWRITE)
	fn(path)

if __name__ == '__main__':
	rmtree('C:/Users/lyolik/AppData/Local/Temp/tmpvbovbo')