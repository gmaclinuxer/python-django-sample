# -*- coding: utf-8 -*-
from common.mymako import render_mako_context
from common.log import logger

from explore.tasks import scheduler


def get_host_details(host_name=None):
    hosts = {
        'proxy': {'user': 'root', 'host': '11.11.1.2', 'password': 'mm', 'port': 22},
        'client1': {'user': 'vagrant', 'host': '11.11.1.3', 'password': 'vagrant', 'port': 22},
        'client2': {'user': 'miya', 'host': '11.11.1.4', 'password': 'miya', 'port': 22},
    }
    if host_name:
        return hosts.get(host_name)

    return [{"%(user)s@%(host)s:%(port)s" % host_detail: host_detail.get('password')}
            for host_detail in hosts.values()]


def get_hosts():
    hosts = {
        'proxy': {'user': 'root', 'host': '11.11.1.2', 'password': 'mm', 'port': 222},
        # 'proxy': {'user': 'vagrant', 'host': '11.11.1.2', 'password': 'vagrant', 'port': 22},
        'client1': {'user': 'vagrant', 'host': '11.11.1.3', 'password': 'vagrant', 'port': 22},
        'client2': {'user': 'miya', 'host': '11.11.1.4', 'password': 'miya', 'port': 22},
    }
    return hosts.values()


def home(request):
    """
    首页
    """
    hosts = get_host_details()
    scheduler.apply_async(args=(0,), kwargs={
        'host_detail': get_host_details('proxy')
    })
    scheduler.apply_async(args=(1,), kwargs={
        'hosts': [host.keys()[0] for host in hosts],
        'passwords': {host.keys()[0]: host.values()[0] for host in hosts}
    })
    scheduler.apply_async(args=(2,), kwargs={
        'hosts': get_hosts()
    })

    # 指定gateway 1
    scheduler.apply_async(args=(3,), kwargs={
        'host_detail': get_host_details('client1'),
        'proxy': get_host_details('proxy'),
    })
    # 指定gateway 2
    # scheduler.apply_async(args=(3,), kwargs={
    #     'host_detail': get_host_details('proxy'),
    #     'proxy': get_host_details('client1'),
    # })

    scheduler.apply_async(args=(4,), kwargs={
        'hosts': [host.keys()[0] for host in hosts],
        'passwords': {host.keys()[0]: host.values()[0] for host in hosts}
    })
    return render_mako_context(request, '/explore/home.html')
