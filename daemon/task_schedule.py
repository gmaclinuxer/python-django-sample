# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import time

# psutil require subprocess
import psutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PID_PATH = BASE_DIR


def get_process_pid(name):
    '''
    获取进程pid
    '''

    file_path = os.path.join(PID_PATH, '%s.pid' % name)
    with open(file_path, 'r') as f:
        pid = f.read()

    try:
        pid = int(pid)
    except:
        pid = -1
    return pid


def get_process_status(name):
    '''
    获取进程状态
    '''

    try:
        pid = get_process_pid(name)
        proc = psutil.Process(pid)
        if proc.status() == psutil.STATUS_ZOMBIE:
            pass
        return proc.status(), proc.pid
    except psutil.NoSuchProcess:
        return 'NoSuchProcess', None
    except IOError:
        return 'IOError', None


def start_process(script_name):
    """
    Starts a process in the background and writes a PID file
    returns integer: pid

    http://stackoverflow.com/questions/7989922/opening-a-process-with-popen-and-getting-the-pid
    Popen.pid The process ID of the child process.
    Note that if you set the shell argument to True, this is the process ID of the spawned shell.
    """

    # /tmp/xxx.py -> xxx
    script_name = os.path.basename(script_name)
    name = os.path.splitext(script_name)[0]

    # Check if the process is already running
    status, pid = get_process_status(name)
    print 'process-%s: %s' % (status, pid)
    if pid is not None and status in [psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING]:
        # must wait for subprocess thread ready
        print 'process-%s exist: %s' % (pid, status)
        return pid

    # start script xxx.py without shell
    # process_shell = subprocess.Popen(path + ' > /dev/null 2> /dev/null &', shell=True)
    # process = subprocess.Popen(['python', script_name], shell=False, stderr=subprocess.STDOUT)
    process = psutil.Popen(['python', script_name], shell=False, stderr=subprocess.STDOUT)
    proc = psutil.Process(process.pid)

    # must wait for subprocess thread ready
    while proc.status() != psutil.STATUS_RUNNING:
        print 'wait process-%s: %s' % (process.pid, proc.status())
        time.sleep(0.3)
    else:
        # record pid to xxx.pid
        file_path = os.path.join(PID_PATH, '%s.pid' % name)
        with open(file_path, 'w') as pidfile:
            pidfile.write(str(process.pid))
        print 'process-%s started.' % process.pid

    return process.pid


def kill_process(script_name):
    """
    kill a process in the background
    """

    # /tmp/xxx.py -> xxx
    script_name = os.path.basename(script_name)
    name = os.path.splitext(script_name)[0]

    # Check if the process is already running
    status, pid = get_process_status(name)
    print 'process-%s: %s' % (status, pid)
    if pid is not None and status in [psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING]:
        # start script xxx.py without shell
        # process_shell = subprocess.Popen(path + ' > /dev/null 2> /dev/null &', shell=True)
        # process = subprocess.Popen(['kill', '-9', str(pid)], shell=False)
        proc = psutil.Process(pid)
        proc.kill()
        try:
            while proc.status() in [psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING]:
                print 'wait process-%s: %s' % (pid, proc.status())
                time.sleep(0.1)
        except psutil.NoSuchProcess:
            pass
        finally:
            # record pid to xxx.pid
            file_path = os.path.join(PID_PATH, '%s.pid' % name)
            if os.path.exists(file_path):
                os.remove(file_path)
            print 'process-%s killed.' % pid
    else:
        print 'process-%s is not running.' % pid


def usage():
    print '''
    Usage: {} scriptname.py <start>|<stop>|<restart>
    '''.format(sys.argv[0])


if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    script_name = sys.argv[1]
    opt_type = sys.argv[2]
    print '%s %s' % (opt_type, script_name)

    if opt_type == 'start':
        start_process(script_name)
    elif opt_type == 'stop':
        kill_process(script_name)
    elif opt_type == 'restart':
        kill_process(script_name)
        start_process(script_name)
    else:
        usage()
        sys.exit(1)
