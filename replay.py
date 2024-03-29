import sys
import argparse
from utils import find_touchscreen, push, execute_command, get_api_version
from exec_cmd import execute_intercept, execute_background
from adbhelper import keep_device_connected


#   replay: push executable and trace file to device, execute in adb
#   trace: trace file generated by getevent -t
#   background: run in detached thread: would not block I/O, kill with kill -9
#   offset: add an offset(ms) to mysendevent actions (-280~-180 seems nice on S6E)
#   delay: (used in record()) delay(s) before executing mysendevent
def replay(trace, background=False, offset=0, delay=0, release_timeout=0.09):
	# args
	exe_local_path = 'mysendevent-arm64'
	exe_remote_path = '/data/local/tmp/mysendevent-arm64'
	trace_local_path = trace
	trace_remote_path = '/data/local/tmp/' + trace

	if option.event == "":
		touch_screen_event = find_touchscreen()
	else:
		touch_screen_event = option.event

	execute_command('adb shell ' + 'cd ' + '/data/local/tmp/')
	push(exe_local_path, exe_remote_path, force=True)
	push(trace_local_path, trace_remote_path, force=True)
	execute_command('adb shell ' + 'chmod +x ' + exe_remote_path)  # 'Permission denied'
	if get_api_version() < 23:
		cmd_string = 'adb shell ' + exe_remote_path + ' -e ' + touch_screen_event + ' -t ' + trace_remote_path + \
					' -o ' + str(offset) + ' -r ' + str(release_timeout) + ' -w '
	else:
		cmd_string = 'adb exec-out ' + exe_remote_path + ' -e ' + touch_screen_event + ' -t ' + trace_remote_path + \
					' -o ' + str(offset) + ' -r ' + str(release_timeout) + ' -w '
	if option.huawei:
		cmd_string += ' -m huawei '
	if option.debug:
		cmd_string += ' -v '

	if background:
		execute_background(cmd_string, delay=delay, outfile=sys.stdout)
	else:
		execute_intercept(cmd_string, delay=delay, outfile=sys.stdout)


if __name__ == '__main__':
	#  parsing arguments
	parser = argparse.ArgumentParser(description="bandori chart replay")
	parser.add_argument('-t', '--trace', action="store", default="", help="path of tracefile")
	parser.add_argument('-o', '--offset', action="store", default="0", help="action offset(ms)")
	parser.add_argument('-d', '--delay', action="store", default="3", help="delay before sendevent(s)")
	parser.add_argument('-n', '--name', action="store", default="", help="device name (shown in adb)")
	parser.add_argument('-e', '--event', action="store", default="", help="touch screen event")
	parser.add_argument('-r', '--release_timeout', action="store", default="0.09", help="release timeout for mysendevent")
	parser.add_argument('--huawei', action="store_true", default=False, help="add support for Huawei devices")
	parser.add_argument('--debug', action="store_true", default=False, help="show verbose details")
	parser.add_argument('--compile', action="store_true", default=False, help="compile mysendevent (dev)")
	option = parser.parse_args()

	# compile mysendevent
	if option.compile:
		execute_command('../../../Desktop/toolchain/bin/aarch64-linux-android-gcc --static mysendevent.c -o mysendevent-arm64', print_to_stdout=True)

	# keep adb happy
	if option.name != '':
		keep_device_connected(option.name)

	print('Delaying', option.delay, 'sec')
	replay(option.trace, offset=int(option.offset), delay=int(option.delay), release_timeout=float(option.release_timeout))
