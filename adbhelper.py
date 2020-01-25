import time
from utils import execute_command


def _restart_adb_server():
	execute_command('adb kill-server')
	execute_command('adb start-server')


def _device_count():
	res_string = execute_command('adb devices')[:-1]  # remove '\n'
	connected_devices = res_string.splitlines()[1:]
	return len(connected_devices)


def _device_checker(connected_devices, device_name):
	device_found = False
	for dev in connected_devices:
		[name_port, status] = dev.split(sep='\t')
		name = name_port.split(sep=':')[0]  # remove port in tcp connection
		if name == device_name:
			device_found = True
			if status == 'offline':  # device offline
				print('[adbhelper] ' + name + ' offline')
				_restart_adb_server()
				execute_command('adb connect ' + device_name, print_to_stdout=True)
		else:
			if str(name_port).find(':') != -1:  # tcp connection
				execute_command('adb disconnect ' + name, print_to_stdout=True)
				print('[adbhelper] ' + name + ' disconnected')
			else:
				print('[adbhelper] cannot disconnect USB devices: plz detach USB cable')
				return False
	if not device_found:  # device not found
		print('[adbhelper] ' + device_name + ' not found')
		execute_command('adb connect ' + device_name, print_to_stdout=True)
	if _device_count() == 1:
		print('[adbhelper] ' + device_name + ' connected')
		return True
	else:
		return False


def keep_device_connected(device_name, delay=3):
	execute_command('adb start-server', print_to_stdout=True)

	res_string = execute_command('adb devices')[:-1]  # remove '\n'
	connected_devices = res_string.splitlines()[1:]
	while _device_checker(connected_devices, device_name) is False:
		print('[adbhelper] Retry after ' + str(delay) + 's')
		time.sleep(delay)
		res_string = execute_command('adb devices')[:-1]  # remove '\n'
		connected_devices = res_string.splitlines()[1:]


if __name__ == '__main__':
	keep_device_connected('192.168.1.103')
