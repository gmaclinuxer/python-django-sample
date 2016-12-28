# -*- coding: utf-8 -*-
from fabric.api import *

# env.roledefs = {
#     'proxy': {
#         'hosts': ['root@11.11.1.2:22'],
#         'role_name': 'miya'
#     },
#     'client': ['vagrant@11.11.1.3:22']
# }

PROMPT = 'Please input your choice:'
running_hosts = {}


def run_command(command):
    with settings(
        hide('running', 'stdout', 'stderr'),
        warn_only=True,
    ):
        if command.strip()[0:5] == "sudo":
            results = sudo(command)
        else:
            results = run(command)
    return results


def get_hosts():
    selected_hosts = []
    for host in raw_input("Hosts (eg: 0|1): ").split():
        selected_hosts.append(env.hosts[int(host)])
    return selected_hosts


def fill_hosts():
    # env.hosts = ['root@11.11.1.2', 'vagrant@11.11.1.3']
    # env.passwords = {
    #     'root@11.11.1.2:22': 'mm',
    #     'vagrant@11.11.1.3:22': 'vagrant',
    # }
    for line in open('ip-list.txt', 'r').readlines():
        host, passw = line.split()
        env.hosts.append(host)
        env.passwords[host] = passw


def list_hosts():
    print u"""ID    | Host                           | Status
    """
    for i, host_string in enumerate(env.hosts):
        print u"""{ID}    | {Host}                           | {Status}
        """.format(ID=i, Host=host_string, Status=running_hosts.get(host_string))


def menu():
    for num, desc in enumerate(["List Hosts", "Run Command", "Open Shell", "Exit"]):
        print "[" + str(num) + "] " + desc
    choice = int(raw_input('\n' + PROMPT))
    while choice != 3:
        list_hosts()
        # If we choose to run a command
        if choice == 1:
            cmd = raw_input("Command: ")
            # Execute the "run_command" task with the given command on the selected hosts
            for host, result in execute(run_command, cmd, hosts=get_hosts()).iteritems():
                print "[" + host + "]: " + cmd
                print ('-' * 80) + '\n' + result + '\n'
        # If we choose to open a shell
        elif choice == 2:
            host = int(raw_input("Host: "))
            execute(open_shell, host=env.hosts[host])
        for num, desc in enumerate(["List Hosts", "Run Command", "Open Shell", "Exit"]):
            print "[" + str(num) + "] " + desc
        choice = int(raw_input('\n' + PROMPT))


def check_hosts():
    """Checks each host to see if it's running"""
    for host, result in execute(run_command, "uptime", hosts=env.hosts).iteritems():
        print result
        running_hosts[host] = result if result.succeeded else "Host Down"


if __name__ == "__main__":
    fill_hosts()
    check_hosts()
    menu()
