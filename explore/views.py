# -*- coding: utf-8 -*-
from django.shortcuts import render

from common.basic import logger

from explore.tasks import scheduler


def get_host_details(host_name=None):
    hosts = {
        'proxy': {'user': 'root', 'host': '11.11.1.2', 'password': 'mm', 'port': 22},
        'client1': {'user': 'vagrant', 'host': '11.11.1.4', 'password': 'vagrant', 'port': 22},
        'client2': {'user': 'miya', 'host': '11.11.1.6', 'password': 'miya', 'port': 22},
    }
    if host_name:
        return hosts.get(host_name)

    return [{"%(user)s@%(host)s:%(port)s" % host_detail: host_detail.get('password')}
            for host_detail in hosts.values()]


def get_hosts():
    hosts = {
        'proxy': {'user': 'root', 'host': '11.11.1.2', 'password': 'mm', 'port': 222},
        # 'proxy': {'user': 'vagrant', 'host': '11.11.1.2', 'password': 'vagrant', 'port': 22},
        'client1': {'user': 'vagrant', 'host': '11.11.1.4', 'password': 'vagrant', 'port': 22},
        'client2': {'user': 'miya', 'host': '11.11.1.6', 'password': 'miya', 'port': 22},
    }
    return hosts.values()


def home(request):
    """
    首页
    """
    # hosts = get_host_details()
    # scheduler.apply_async(args=(0,), kwargs={
    #     'host_detail': get_host_details('proxy')
    # })
    # scheduler.apply_async(args=(1,), kwargs={
    #     'hosts': [host.keys()[0] for host in hosts],
    #     'passwords': {host.keys()[0]: host.values()[0] for host in hosts}
    # })
    # scheduler.apply_async(args=(1,), kwargs={
    #     'hosts': [host.keys()[0] for host in hosts],
    #     'passwords': {host.keys()[0]: 'task1' for host in hosts}
    # })
    # scheduler.apply_async(args=(2,), kwargs={
    #     'hosts': get_hosts()
    # })

    # 指定gateway
    scheduler.apply_async(args=(3,), kwargs={
        'host_detail': get_host_details('client1'),
        'proxy': get_host_details('proxy'),
    })
    return render(request, 'explore.html')
