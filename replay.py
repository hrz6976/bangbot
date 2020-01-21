import subprocess
from utils import find_touchscreen, push, exec


def replay(exe_local_path, trace_local_path, exe_remote_path, trace_remote_path):
	touch_screen_event = find_touchscreen()
	exec('cd ' + '/data/local/tmp/')
	push(exe_local_path, exe_remote_path)
	push(trace_local_path, trace_remote_path, force=True)
	exec('chmod +x ' + exe_remote_path)  # 'Permission denied'
	cmd_string = 'adb shell ' + exe_remote_path + ' ' + touch_screen_event + ' ' + trace_remote_path
	process = subprocess.Popen(cmd_string.split(), stdout=subprocess.STDOUT)
	input('Press Enter to stop')
	process.terminate()


if __name__ == '__main__':
	replay('mysendevent-arm64', 'trace01.txt', '/data/local/tmp/mysendevent-arm64', '/data/local/tmp/trace01.txt')
