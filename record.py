import logging
import os
import time
from utils import find_touchscreen, get_api_version
from exec_cmd import execute_intercept
from replay import replay


def record(outfile=None):
	# Try to solve tap missing issue: use exec-out on higher level api
	touch_screen_event = find_touchscreen()
	if get_api_version() < 23:
		cmd_string = 'adb shell getevent -t ' + touch_screen_event
	else:
		cmd_string = 'adb exec-out getevent -t ' + touch_screen_event
	print("Start recording")
	res = execute_intercept(cmd_string, outfile)
	print("Finished recording")
	return str(res)


def extract_botton_pos(res_string):
	print(res_string)
	x_index = res_string.find('0003 0035')
	y_index = res_string.find('0003 0036')
	if x_index < 0 or y_index < 0:
		logging.warning("ABS_MT_POSITION not found. Make sure you touched the screen.")
		return ['Failed', 'Failed']
	x = res_string[x_index+10:x_index+18]
	y = res_string[y_index+10:y_index+18]
	logging.debug('botton_pos='+'['+x+','+y+']')
	return [x, y]


def grab_botton_pos():
	_res_string = record()
	_botton_pos = extract_botton_pos(_res_string)
	while _botton_pos is ['Failed', 'Failed']:
		print('Make sure you have touched the screen. Trying again...')
		_res_string = record()
		_botton_pos = extract_botton_pos(_res_string)
	return _botton_pos


def fill_start_trace(coord, times, interval, t_init, file_obj):
	t = t_init
	for _ in range(times):
		print('[', str(round(t, 6)).rjust(15), '] 0003 0039 00002fff', file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0001 014a 00000001', file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0001 0145 00000001', file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0003 0035', coord[0], file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0003 0036', coord[1], file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0000 0000 00000000', file=file_obj)
		t += interval/2
		print('[', str(round(t, 6)).rjust(15), '] 0003 0039 ffffffff', file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0001 014a 00000000', file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0001 0145 00000000', file=file_obj)
		print('[', str(round(t, 6)).rjust(15), '] 0000 0000 00000000', file=file_obj)
		t += interval/2
	return t


def gen_start_trace(start_coord, pause_coord, continue_coord, dest):
	with open(dest, 'w') as f:
		t = 0
		t = fill_start_trace(start_coord, 1, 0.5, t, f)
		t += 7
		t = fill_start_trace(pause_coord, 500, 0.02, t, f)
		t = fill_start_trace(continue_coord, 1, 0.5, t, f)


def first_run(dest):
	print('Tap on "start" then press ENTER')
	start_coord = grab_botton_pos()
	print('Tap on "pause" then press ENTER')
	pause_coord = grab_botton_pos()
	print('Tap on "continue" then press ENTER')
	continue_coord = grab_botton_pos()
	print('start_coord:', start_coord)
	print('pause_coord:', pause_coord)
	print('continue_coord:', continue_coord)
	gen_start_trace(start_coord, pause_coord, continue_coord, dest)


if __name__ == '__main__':
	# Make life easier
	start_trace_path = 'trace_start.txt'

	# debug
	_start_coord = ['0000040a', '000003d5']  # coords on Samsung S6E
	_pause_coord = ['0000007a', '0000003a']
	_continue_coord = ['00000386', '000003ad']
	gen_start_trace(_start_coord, _pause_coord, _continue_coord, start_trace_path)

	if not os.path.isfile(start_trace_path):
		print("Start trace not found")
		first_run(start_trace_path)
		print("Start trace generated. Plz run again.")
		exit(0)
	replay(start_trace_path, background=True)
	with open('trace_01.txt', 'w') as f:
		record(outfile=f)
