import time
import subprocess
import threading
import logging

_res_string = ''  # Safe: 1 worker writes to it at the same time
logging.basicConfig(level=logging.WARNING)  # change DEBUG to WARNING if not debugging


#   stop_activated: thread event val
#   cmd_string: exec cmd (shell option is removed for security)
#               subprocess.Popen can't run pipe commands '|'
#   outfile: send output to a file (i.e. sys.stdout)
#            _res_string = '' when outfile is not None
#   delay: delay(s) before executing command
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
				logging.warning("[exec_cmd] Thread failed to terminate. Using SIGKILL")
				process.kill()
			if outfile is None:
				global _res_string
				_res_string = process.stdout.read().decode('utf-8')
			return
	logging.debug('\n[exec_cmd] ' + cmd_string + ' stopped normally')


#   listen for ENTER then set thread event
#   ENTER might not be captured when logging level set to DEBUG: try ENTER again
def _keypress_listener(stop_activated):
	input()
	print("[keypress_listener] ENTER caught")
	stop_activated.set()


#   join worker thread: block before worker exit
#   send args to _worker()
#   return _res_string changed by _worker()
def execute_intercept(cmd_string, outfile=None, delay=0):
	stop_activated = threading.Event()
	thread_worker = threading.Thread(target=_worker, args=(stop_activated, cmd_string, outfile, delay))
	thread_worker.start()
	kill_listener = threading.Thread(target=_keypress_listener, args=(stop_activated,), daemon=True)
	kill_listener.start()
	logging.debug('\n' + cmd_string + ' starting\n> intercept with ENTER')
	thread_worker.join()

	global _res_string
	return _res_string


#   DOES NOT return
#   detached threads can not be killed with SIGINT: use kill -9
def execute_background(cmd_string, outfile=None, delay=0):
	stop_activated = threading.Event()
	thread_worker = threading.Thread(target=_worker, args=(stop_activated, cmd_string, outfile, delay))
	thread_worker.start()
	logging.debug('\n' + cmd_string + ' starting:\n> delay ' + str(delay) + 's \n> kill with kill -9')


if __name__ == '__main__':
	execute_intercept('adb exec-out getevent -t /dev/input/event1')
