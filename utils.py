import subprocess


#   return touch_screen_event(str)
#   ref:https://stackoverflow.com/questions/54228228/adb-how-to-programmatically-determine-which-input-device-is-used-for-sending-to
#   Modified: return bottom line, remove '\n'
#   Issues found with Samsung S10 (API29): Using string as RS in awk: only first char takes effect
def find_touchscreen():
    cmd_string = 'adb shell ' + "getevent -pl | grep -B 100 ABS_MT_POSITION_X | \
    awk '/add device/ {print $NF}' | awk 'END {print}'"
    out_bytes = subprocess.check_output(cmd_string.split())
    return out_bytes.decode('utf-8')[:-1]  # remove '\n'


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
def push(local_path, remote_path, force=False):
    if force is False:
        cmd_string = 'adb shell [ -e ' + remote_path + ' ] && echo "Found" || echo "NotFound"'
        out_bytes = subprocess.check_output(cmd_string.split())
        if out_bytes.decode('utf-8') is not 'Found\n':
            cmd_string = 'adb push ' + local_path + ' ' + remote_path
            subprocess.check_output(cmd_string.split())
    else:
        cmd_string = 'adb push ' + local_path + ' ' + remote_path
        subprocess.check_output(cmd_string.split())


if __name__ == '__main__':
    print(find_touchscreen())
    print(get_api_version())
    push('mysendevent-arm64', '/data/local/tmp/mysendevent-arm64')
