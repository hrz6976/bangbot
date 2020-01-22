from utils import find_touchscreen, push, execute_adb_shell
from exec_cmd import execute_intercept, execute_background


def replay(trace, background=False):
	# Make life easier
	exe_local_path = 'mysendevent-arm64'
	exe_remote_path = '/data/local/tmp/mysendevent-arm64'
	trace_local_path = trace
	trace_remote_path = '/data/local/tmp/' + trace

	touch_screen_event = find_touchscreen()
	execute_adb_shell('cd ' + '/data/local/tmp/')
	push(exe_local_path, exe_remote_path)
	push(trace_local_path, trace_remote_path, force=True)
	execute_adb_shell('chmod +x ' + exe_remote_path)  # 'Permission denied'
	cmd_string = 'adb shell ' + exe_remote_path + ' ' + touch_screen_event + ' ' + trace_remote_path
	if background:
		execute_background(cmd_string, delay=5)
	else:
		execute_intercept(cmd_string)


if __name__ == '__main__':
	replay('trace_01.txt')
