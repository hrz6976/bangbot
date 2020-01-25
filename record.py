import logging
import argparse
from utils import find_touchscreen, get_api_version
from exec_cmd import execute_intercept
from adbhelper import keep_device_connected


#   outfile=None: return result(str)
#   outfile=f: (i.e. sys.stdout) send output to f, result =''
def record(outfile=None):
	# Try to solve tap missing issue: use exec-out on higher level api
	touch_screen_event = find_touchscreen()
	logging.debug('Found touchscreen: ' + touch_screen_event)
	if get_api_version() < 23:
		cmd_string = 'adb shell getevent -t ' + touch_screen_event
	else:
		cmd_string = 'adb exec-out getevent -t ' + touch_screen_event
	print("Start recording, press ENTER to stop")
	res = execute_intercept(cmd_string, outfile)
	print("Finish recording")
	return str(res)


if __name__ == '__main__':
	#  parsing arguments
	parser = argparse.ArgumentParser(description="bandori chart record")
	parser.add_argument('-t', '--trace', action="store", default="", help="path of tracefile")
	parser.add_argument('-n', '--name', action="store", default="", help="device name (shown in adb)")
	parser.add_argument('--debug', action="store_true", default=False, help="show verbose details")
	option = parser.parse_args()

	# keep adb happy
	if option.name != '':
		keep_device_connected(option.name)

	with open(option.trace, 'w') as f:
		print('Press ENTER, then start playing DIRECTLY')
		input()
		record(outfile=f)
		print("Saving to", f.name)
