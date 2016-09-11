# -*- coding: utf-8 -*-
import datetime
from django.db import models


# Create your models here.


class MonthlyWeatherByCity(models.Model):
    month = models.IntegerField()
    boston_temp = models.DecimalField(max_digits=5, decimal_places=1)
    houston_temp = models.DecimalField(max_digits=5, decimal_places=1)
    new_york_temp = models.DecimalField(max_digits=5, decimal_places=1)
    san_franciso_temp = models.DecimalField(max_digits=5, decimal_places=1)


class MonthlyWeatherSeattle(models.Model):
    month = models.IntegerField()
    seattle_temp = models.DecimalField(max_digits=5, decimal_places=1)


class DailyWeather(models.Model):
    month = models.IntegerField()
    day = models.IntegerField()
    temperature = models.DecimalField(max_digits=5, decimal_places=1)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Publisher(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s' % (self.name)


class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s' % (self.name)


class Book(models.Model):
    title = models.CharField(max_length=50)
    rating = models.FloatField(db_column='rating')
    rating_count = models.IntegerField()
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, null=True, blank=True,
                                  on_delete=models.SET_NULL)
    related = models.ManyToManyField('self', db_column='related', blank=True)
    genre = models.ForeignKey(Genre, null=True, blank=True,
                              on_delete=models.SET_NULL)

    def __unicode__(self):
        return '%s' % (self.title)


class City(models.Model):
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)

    def __unicode__(self):
        return '%s, %s' % (self.city, self.state)


class BookStore(models.Model):
    name = models.CharField(max_length=50)
    city = models.ForeignKey('City')

    def __unicode__(self):
        return '%s' % (self.name)


class SalesHistory(models.Model):
    bookstore = models.ForeignKey(BookStore)
    book = models.ForeignKey(Book)
    sale_date = models.DateField()
    sale_qty = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __unicode__(self):
        return '%s %s %s' % (self.bookstore, self.book, self.sale_date)
##########################################################################
# 安装脚本错误码
##########################################################################
UNKNOWN = 0  # 没有错误的错误码
APP_EXCP = 10001
LOGIN_TIMEOUT_ERR = 10002
WRONG_PASSWORD = 10003
WRONG_PORT = 10004
SSH_LOGIN_EXCP = 10005
PROXY_UNUSEABLE = 10006
CELERY_TASK_EXCP = 10007
LOGIN_FAILED = 10008
SEND_KEY_EXCP = 10009
AUTH_WAY_ERROR = 10010
UPLOAD_EXCP = 10011
CON_REFUSED = 10012
KEY_MODE_ERR = 10013
KEY_ERR = 10014
UNEXPECT_RETURN = 10015
COMMON_ERROR = 10016
LOGIN_NOT_SUPPORT = 10017
P2P_FAILED = 10018
UPLOAD_RETRY = 10019
UPLOAD_ERR = 10020
AGENT_NOT_EXIST = 10021             # 拨测作业下发前，查询agent状态超时未连线，可重试
DIAL_EXCP = 10022                   # 拨测作业异常，可重试
DIAL_FAIL = 10023                   # 拨测作业启动失败，基本不可重试
DIAL_TIMEOUT_ERR = 10024            # 作业下发后查询拨测结果超时，可重试
MARK_FAIL = 10025                   # 反写CC失败，基本不可重试
TORRENT_NOT_EXIST = 10026
FILES_NOT_EXIST = 10027
GENERATE_FILE_ERR = 10028
EXECUTE_ERR = 10029
IJOBS_FAIL = 10030                  # 执行ijobs作业失败
FORCE_STOP = 10031                  # 强制结束
UPLOAD_TIMEOUT_ERR = 10032          # 文件上传超时
SOCKET_TIMEOUT_ERR = 10033          # socket.timeout
JOB_TIMEOUT_ERR = 10034             # lunxun timeout
P2P_TIMEOUT_ERR = 10035             # P2P下载超时
# 安装失败状态
INSTALL_FAILED = -1
CHECK_OS_FAILED = -2
MODIFY_CONF_FAILED = -3
CHECK_USER_FAILED = -4
COPY_FAILED = -5
TAR_XF_FAILED = -6
TELNET_SERVER_PORT_FAILED = -7
EXE_FILE_NOT_EXISTS = -8
COPY_TEMPLATE_FAILED = -9
CHECK_RUNMODE_FAILED = -10
CHECK_IPV6_FAILED = -11
# 继续安装，可忽略状态
TELNET_FAILED = -12
ADD_IPTABLES_FAILED = -13
SCRIPT_TIMEOUT_ERR = -14
LOGON_TIMEOUT = -15
NO_ROUTE_TO_HOST = -16
NO_SUCH_FILE_DIRECTORY = -10000
STILL_RUNNING = 999
SUCCESS = 666
# 错误码解释
ERR_CODE = [
    (UNKNOWN, 'UNKNOWN'),
    (DIAL_FAIL, 'DIAL_FAIL'),
    (DIAL_EXCP, 'DIAL_EXCP'),
    (AGENT_NOT_EXIST, 'AGENT_NOT_EXIST'),
    (FILES_NOT_EXIST, 'FILES_NOT_EXIST'),
    (UPLOAD_ERR, 'UPLOAD_ERR'),
    (PROXY_UNUSEABLE, 'PROXY_UNUSEABLE'),
    (UPLOAD_RETRY, 'UPLOAD_RETRY'),
    (LOGIN_FAILED, 'LOGIN_FAILED'),
    (LOGON_TIMEOUT, 'LOGON_TIMEOUT'),
    (SEND_KEY_EXCP, 'SEND_KEY_EXCP'),
    (AUTH_WAY_ERROR, 'AUTH_WAY_ERROR'),
    (UPLOAD_EXCP, 'UPLOAD_EXCP'),
    (P2P_FAILED, 'P2P_FAILED'),
    (TORRENT_NOT_EXIST, 'TORRENT_NOT_EXIST'),
    (IJOBS_FAIL, 'IJOBS_FAIL'),
    (EXECUTE_ERR, 'EXECUTE_ERR'),
    (DIAL_TIMEOUT_ERR, 'DIAL_TIMEOUT_ERR'),
    (MARK_FAIL, 'MARK_FAIL'),
    (GENERATE_FILE_ERR, 'GENERATE_FILE_ERR'),
    (SUCCESS, 'SUCCESS'),
    (LOGIN_NOT_SUPPORT, 'LOGIN_NOT_SUPPORT'),
    (KEY_MODE_ERR, 'KEY_MODE_ERR'),
    (KEY_ERR, 'KEY_ERR'),
    (NO_SUCH_FILE_DIRECTORY, 'NO_SUCH_FILE'),
    (LOGIN_TIMEOUT_ERR, 'LOGIN_TIMEOUT_ERR'),
    (JOB_TIMEOUT_ERR, 'JOB_TIMEOUT_ERR'),
    (SCRIPT_TIMEOUT_ERR, 'SCRIPT_TIMEOUT_ERR'),
    (UPLOAD_TIMEOUT_ERR, 'UPLOAD_TIMEOUT_ERR'),
    (P2P_TIMEOUT_ERR, 'P2P_TIMEOUT_ERR'),
    (COMMON_ERROR, 'COMMON_ERROR'),
    (UNEXPECT_RETURN, 'UNEXPECT_RETURN'),
    (CON_REFUSED, 'CON_REFUSED'),
    (WRONG_PASSWORD, 'WRONG_PASSWORD'),
    (WRONG_PORT, 'WRONG_PORT'),
    (SSH_LOGIN_EXCP, 'SSH_LOGIN_EXCP'),
    (APP_EXCP, 'APP_EXCP'),
    (FORCE_STOP, 'FORCE_STOP'),
    (PROXY_UNUSEABLE, 'PROXY_UNUSEABLE'),
    (CELERY_TASK_EXCP, 'CELERY_TASK_EXCP'),
    (AUTH_WAY_ERROR, 'AUTH_WAY_ERROR'),
    (STILL_RUNNING, 'STILL_RUNNING'),
    (INSTALL_FAILED, 'INSTALL_FAILED'),
    (CHECK_OS_FAILED, 'CHECK_OS_FAILED'),
    (MODIFY_CONF_FAILED, 'MODIFY_CONF_FAILED'),
    (TELNET_FAILED, 'TELNET_FAILED'),
    (CHECK_USER_FAILED, 'CHECK_OS_FAILED'),
    (ADD_IPTABLES_FAILED, 'ADD_IPTABLES_FAILED'),
    (COPY_FAILED, 'COPY_FAILED'),
    (TAR_XF_FAILED, 'TAR_XF_FAILED'),
    (TELNET_SERVER_PORT_FAILED, 'TELNET_SERVER_PORT_FAILED'),
    (EXE_FILE_NOT_EXISTS, 'EXE_FILE_NOT_EXISTS'),
    (COPY_TEMPLATE_FAILED, 'COPY_TEMPLATE_FAILED'),
    (CHECK_RUNMODE_FAILED, 'CHECK_RUNMODE_FAILED'),
    (CHECK_IPV6_FAILED, 'CHECK_IPV6_FAILED'),
    (NO_ROUTE_TO_HOST, 'NO_ROUTE_TO_HOST'),
]

import random
ERR_LIST = [_[0] for _ in ERR_CODE]
ERR_DICT = dict(ERR_CODE)

class FailedStat(models.Model):

    ip = models.GenericIPAddressField(u'主机内网IP', max_length=128)
    err_code = models.SmallIntegerField(u'安装失败错误码', choices=ERR_CODE, default=0)
    type = models.SmallIntegerField(u'机器类型', choices=[(0, 'proxy'),(1, 'agent')], default=0)
    create_time = models.DateTimeField(u'安装失败时间', auto_now_add=True)

    def __unicode__(self):
        return u'%s-%s-%s' % (self.ip, self.err_code, self.create_time)

    @classmethod
    def random(cls, size):
        for i in range(size):
            FailedStat.objects.create(
                ip='{seg}.{seg}.{seg}.{seg}'.format(seg=random.randint(1, 254)),
                err_code=random.choice(ERR_LIST),
                type=random.choice([0, 1]),
                create_time=datetime.datetime.now() + datetime.timedelta(days=i)
            )
    class Meta:
        verbose_name = u'安装失败统计表'
        verbose_name_plural = u'安装失败统计表'
