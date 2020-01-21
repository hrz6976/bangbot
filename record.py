import subprocess
from utils import find_touchscreen, get_api_version


def record(dest):
	touch_screen_event = find_touchscreen()
	# Try to fix missing key issues on newer device
	if get_api_version() < 23:
		cmd_string = 'adb shell getevent -t ' + touch_screen_event
	else:
		cmd_string = 'adb exec-out getevent -t ' + touch_screen_event
	with open(dest, 'w') as f:
		process = subprocess.Popen(cmd_string.split(), stdout=f)
		input('Press Enter to stop')
		process.terminate()
	# print('Ctrl+C to stop')
	# sub = subprocess.Popen(cmd_string.split(), stdout=subprocess.PIPE)
	# lines = []  # Need someplace to store the data as it comes
	# try:
	# 	for line in sub.stdout:  # read one line from standard out, store it in lines
	# 		lines.append(line.decode('utf-8'))
	# except KeyboardInterrupt:  # keyboardInterrupt happened.  Stop process
	# 	sub.terminate()
	# finally:  # Join our lines into a single buffer (like `communicate`)
	# 	output = ''.join(lines)
	# 	del lines
	# return output


# def record(dest):
# 	res = record_worker()
# 	with open(dest, 'w') as f:
# 		for line in record_worker():
# 			print(line, file=f)


if __name__ == '__main__':
	record('trace01.txt')
