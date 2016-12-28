# -*- coding: utf-8 -*-
import json
import os
from fabric.api import cd, lcd, run, local, env, hosts, settings, abort, parallel, roles, sudo
from fabric.context_managers import prefix
from fabric.contrib.console import confirm
# from fabric.decorators import with_settings
from fabric.operations import put

u"""
fab -f fab_helloworld.py hello:Jeff
"""


def hello(name="world"):
    local('echo in hello')
    print("Hello %s!" % name)

    # 错误忽略
    with settings(warn_only=True):
        run('whoami')
        with cd('../'):
            lr = local('ls ./', capture=True)
            if lr.failed and not confirm('task failed. Continue anyway?'):
                abort('you choose abort current task.')
    local('echo out hello')

u"""
自定义user/host/passowrd 局部方式：
"""
@hosts('vagrant@11.11.1.3:22')
# @with_settings(password='vagrant')
def deploy():
    deploy_dir = '/tmp/explore/'
    password = 'vagrant'
    with settings(password=password, warn_only=True):
        with prefix('ifconfig -a'):
            run('whoami')
        with cd('/tmp'):
            rc = run('[ -d {deploy_dir} ] || mkdir {deploy_dir} -p'.format(deploy_dir=deploy_dir))
            if rc.failed and not confirm('task failed, Continued anyway?'):
                abort('you give up')
            put(__file__, deploy_dir)

env.roledefs = {
    'proxy': {
        'hosts': ['root@11.11.1.2:22'],
        'role_name': 'miya'
    },
    'client': ['vagrant@11.11.1.3:22']
}
env.password = 'global_password'
# env.key_filename = 'id_rsa'
# env.sudo_user = 'vagrant'
# env.sudo_password = 'vagrant'
# env.sudo_passwords = {
#     'host_string': 'password'
# }
# http://docs.fabfile.org/en/1.4.0/usage/execution.html#roles
env.roledefs['all'] = [h for r in env.roledefs.values() for h in r]

# @hosts('root@11.11.1.2:22')
@roles('proxy')
def deploy1():
    password = 'mm'
    print json.dumps(env, indent=2)
    print os.environ.get('role_name')
    with settings(password=password):
        run('whoami')
        run('ifconfig -a')


u"""
自定义user/host/passowrd 全局方式：
"""
# env.user = 'vagrant'
env.hosts = ['root@11.11.1.2', 'vagrant@11.11.1.3']
env.passwords = {
    'vagrant@11.11.1.2:22': 'vagrant',
    'root@11.11.1.3:22': 'mm',
}

# https://github.com/fabric/fabric/issues/489 not support on windows for parallel
# @parallel(pool_size=5)
def deploy2():
    run('whoami')
    put('./f53', '/tmp')
    run('ifconfig -a')




