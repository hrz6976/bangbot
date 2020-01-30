import subprocess
import os


#   return touch_screen_event(str)
#   ref:https://stackoverflow.com/questions/54228228/adb-how-to-programmatically-determine-which-input-device-is-used-for-sending-to
#   some older devices does not implement awk
#   execute in shell: compatibility
#   replaced tail with sed: old devices didn't get it
#   I/O redirction now compatible with win32
def find_touchscreen():
    if os.name == 'nt':  # win32
        cmd_string = "adb shell getevent -lp | adb shell grep -B 100 ABS_MT_POSITION_X | " \
                     "adb shell grep '/dev/input/event' | adb shell sed -e 's/^add\ device\ [0-9]\{1,2\}:\ //' | " \
                     "adb shell sed '$!d'"
    else:  # posix or jvm
        cmd_string = "adb shell getevent -lp | grep -B 100 ABS_MT_POSITION_X | " \
                     "grep '/dev/input/event' | sed -e 's/^add device [0-9]\{1,2\}: //' | sed '$!d'"
    res_string = subprocess.check_output(cmd_string, shell=True).decode('utf-8')[:-1]
    return res_string


#   return device api version(int)
def get_api_version():
    cmd_string = 'adb shell ' + 'getprop ro.build.version.sdk'
    out_bytes = subprocess.check_output(cmd_string.split())
    res = int(out_bytes.decode('utf-8'))
    return res


#   execute adb shell command, return result(str)
def execute_command(cmd_string, print_to_stdout=False):
    if print_to_stdout is False:
        return subprocess.check_output(cmd_string.split()).decode('utf-8')
    else:
        subprocess.call(cmd_string.split())


#   local_path, remote_path include filename
#   force=False: check if file exists before push
#   execute in shell: compatibility
def push(local_path, remote_path, force=False):
    if force is False:
        cmd_string = 'adb shell [ -e ' + remote_path + ' ] && echo "Found" || echo "NotFound"'
        out_bytes = subprocess.check_output(cmd_string.split())
        if out_bytes.decode('utf-8') is not 'Found\n':
            cmd_string = 'adb push ' + local_path + ' ' + remote_path
            subprocess.check_output(cmd_string, shell=True)
    else:
        cmd_string = 'adb push ' + local_path + ' ' + remote_path
        subprocess.check_output(cmd_string, shell=True)


if __name__ == '__main__':
    print(find_touchscreen())
    print(get_api_version())
    push('mysendevent-arm64', '/data/local/tmp/mysendevent-arm64')
