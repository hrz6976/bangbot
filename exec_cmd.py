import time
import subprocess
import threading
import logging

_res_string = ''  # Safe: 1 worker writes to it at the same time
logging.basicConfig(level=logging.DEBUG)  # change DEBUG to WARNING if not debugging


# _res_string = '' when outfile is set
# subprocess.Popen can't run pipe cmds '|'
def _worker(stop_activated, cmd_string, outfile=None, delay=0):
	time.sleep(delay)
	if outfile is None:
		process = subprocess.Popen(cmd_string.split(), stdout=subprocess.PIPE)
	else:
		process = subprocess.Popen(cmd_string.split(), stdout=outfile)
	while process.poll() is None:
		time.sleep(0.5)  # Not the best way to do it, however signal functions are OS-dependent
		if stop_activated.is_set():
			logging.debug("Stopping thread via SIGTREM")
			process.terminate()
			time.sleep(0.5)
			if process.poll() is None:
				logging.warning("Thread failed to terminate. Using SIGKILL")
				process.kill()
			if outfile is None:
				global _res_string
				_res_string = process.stdout.read().decode('utf-8')
			return
	logging.debug('\n' + cmd_string + ' stopped normally')


def _keypress_listener(stop_activated):
	input("Press ENTER to stop")
	print("ENTER intercepted")
	stop_activated.set()


def execute_intercept(cmd_string, outfile=None, delay=0):
	stop_activated = threading.Event()
	thread_worker = threading.Thread(target=_worker, args=(stop_activated, cmd_string, outfile, delay))
	thread_worker.start()
	kill_listener = threading.Thread(target=_keypress_listener, args=(stop_activated,), daemon=True)
	kill_listener.start()
	logging.debug('\n' + cmd_string + ' starting: intercept with ENTER')
	thread_worker.join()

	global _res_string
	return _res_string


# detached threads can not be killed with SIGINT: use kill -9
def execute_background(cmd_string, outfile=None, delay=0):
	stop_activated = threading.Event()
	thread_worker = threading.Thread(target=_worker, args=(stop_activated, cmd_string, outfile, delay))
	thread_worker.start()
	logging.debug('\n' + cmd_string + ' starting: kill with kill -9')


if __name__ == '__main__':
	execute_intercept('adb exec-out getevent -t /dev/input/event1')
