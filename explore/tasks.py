# -*- coding: utf-8 -*-
"""
https://coderwall.com/p/5kq4tq/fabric-and-celery-can-be-friends
http://stackoverflow.com/questions/16921357/fabric-how-to-supply-ssh-password-dynamically
http://raidersec.blogspot.com/2013/07/building-ssh-botnet-c-using-python-and.html
more:
    http://tav.espians.com/fabric-python-with-cleaner-api-and-parallel-deployment-support.html
"""
import time
from celery.task import task
from celery.utils.log import get_task_logger
from fabric.api import env, hosts, roles, run, execute, settings, hide, sudo, with_settings
logger = get_task_logger(__name__)


# http://docs.fabfile.org/en/1.4.0/usage/execution.html#roles
env.skip_bad_hosts = True
env.warn_only = True

def run_command(command):
    """
    auto select run or sudo
    """
    with hide('running', 'stdout', 'stderr'):
        if command.strip()[0:5] == "sudo":
            results = sudo(command)
        else:
            results = run(command)
    return results


@task()
def celery_task(**kwargs):
    host_detail = kwargs.get('host_detail')
    # python-string-format-with-dict-with-integer-keys
    host_string = "%(user)s@%(host)s:%(port)s" % host_detail

    @hosts(host_string)
    def fab_task():
        with settings(password=host_detail.get('password')):
            # time.sleep(10)
            logger.info(u'\n================================================\n')
            results = run_command("hostname")
            logger.info(results)

    # Fabric has a fail-fast execution policy, let's catch it
    try:
        result = execute(fab_task)
        logger.warning(u'【host_string】: %s' % result)
        if isinstance(result.get(host_string, None), BaseException):
            raise result.get(host_string)
    except Exception as e:
        logger.error(u"celery_task(Exception): %s" % e.message)


@task()
def celery_task1(**kwargs):
    host_list = kwargs.get('hosts')
    # will change env.passwords and effect other task because env is module global
    env.passwords = kwargs.get('passwords')
    # Fabric has a fail-fast execution policy, let's catch it
    try:
        for host_string, result in execute(run_command, 'hostname', hosts=host_list).iteritems():
            logger.warning('%s\n:%s' % ('='*10, env.passwords))
            logger.info(result)
    except Exception as e:
        logger.error(u"celery_task(Exception): %s" % e.message)


def run_cmd_with_passwd(command, passwd):
    """
    auto select run or sudo
    """
    # host_string = "%(user)s@%(host)s:%(port)s" % host
    with settings(
        hide('running', 'stdout', 'stderr'),
        # host_string=host_string,
        # password=host.get('password'),
        password=passwd,
        warn_only=True
    ):
        if command.strip()[0:5] == "sudo":
            results = sudo(command)
        else:
            results = run(command)
    return results

@task()
def celery_task2(**kwargs):
    # Fabric has a fail-fast execution policy, let's catch it
    try:
        for host in kwargs.get('hosts'):
            host_string = "%(user)s@%(host)s:%(port)s" % host
            result = execute(run_cmd_with_passwd, 'hostname', host.get('password'), hosts=[host_string])
            logger.info(result)
            if isinstance(result.get(host_string, None), BaseException):
                raise result.get(host_string)
    except Exception as e:
        logger.error(u"celery_task(Exception): %s" % e.message)


@task()
def celery_task3(**kwargs):
    host_detail = kwargs.get('host_detail')
    gateway = kwargs.get('proxy')
    host_string = "%(user)s@%(host)s:%(port)s" % host_detail
    gateway_host_string = "%(user)s@%(host)s:%(port)s" % gateway

    @hosts(host_string)
    @with_settings(
        passwords={
            'root@11.11.1.2:22': 'mm',
            'vagrant@11.11.1.4:22': 'vagrant'
        },
        gateway=gateway_host_string
    )
    def fabgw_task():
        results = run_command("who")
        logger.info(results)

    # Fabric has a fail-fast execution policy, let's catch it
    try:
        result = execute(fabgw_task)
        logger.warning(u'【host_string】: %s' % result)
        if isinstance(result.get(host_string, None), BaseException):
            raise result.get(host_string)
    except Exception as e:
        logger.error(u"celery_task3(Exception): %s" % e.message)

@task(ignore_result=True)
def scheduler(task_type, **kwargs):
    logger.info(u'task_type: %s' % task_type)
    if task_type == 0:
        return None
        celery_task.apply_async(kwargs=kwargs)
    if task_type == 1:
        return None
        celery_task1.apply_async(kwargs=kwargs)
    if task_type == 2:
        return None
        celery_task2.apply_async(kwargs=kwargs)
    if task_type == 3:
        celery_task3.apply_async(kwargs=kwargs)

if __name__ == '__main__':
    print 'test'
