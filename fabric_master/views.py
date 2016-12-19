# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

from fabric.api import run, execute, task, env, hosts
from fabric.context_managers import settings, hide

from common.basic import logger

task_hosts = ('11.11.1.2', '11.11.1.4', '11.11.1.6')
env.hosts = task_hosts
env.user = 'vagrant'
env.password = 'vagrant'


@task
# @hosts(task_hosts)
def mytask():
    with settings(warn_only=True):
        run('ifconfig -a')

def mytask1():
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):
        if run('ls /etc/lsb-release'):
            return 'Ubuntu'
        elif run('ls /etc/redhat-release'):
            return 'RedHat'

def home(request):
    try:
        r = execute(mytask, hosts=task_hosts[:])
        print r
    except Exception as e:
        logger.error(e)
        print e
    return JsonResponse({'result': True, 'data': [], 'message': u'operate successfully.'})
