# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('rating', models.FloatField(db_column=b'rating')),
                ('rating_count', models.IntegerField()),
                ('authors', models.ManyToManyField(to='chartapp.Author')),
            ],
        ),
        migrations.CreateModel(
            name='BookStore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='DailyWeather',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.IntegerField()),
                ('day', models.IntegerField()),
                ('temperature', models.DecimalField(max_digits=5, decimal_places=1)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='FailedStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(verbose_name='\u4e3b\u673a\u5185\u7f51IP')),
                ('err_code', models.SmallIntegerField(default=0, verbose_name='\u5b89\u88c5\u5931\u8d25\u9519\u8bef\u7801', choices=[(0, b'UNKNOWN'), (10023, b'DIAL_FAIL'), (10022, b'DIAL_EXCP'), (10021, b'AGENT_NOT_EXIST'), (10027, b'FILES_NOT_EXIST'), (10020, b'UPLOAD_ERR'), (10006, b'PROXY_UNUSEABLE'), (10019, b'UPLOAD_RETRY'), (10008, b'LOGIN_FAILED'), (-15, b'LOGON_TIMEOUT'), (10009, b'SEND_KEY_EXCP'), (10010, b'AUTH_WAY_ERROR'), (10011, b'UPLOAD_EXCP'), (10018, b'P2P_FAILED'), (10026, b'TORRENT_NOT_EXIST'), (10030, b'IJOBS_FAIL'), (10029, b'EXECUTE_ERR'), (10024, b'DIAL_TIMEOUT_ERR'), (10025, b'MARK_FAIL'), (10028, b'GENERATE_FILE_ERR'), (666, b'SUCCESS'), (10017, b'LOGIN_NOT_SUPPORT'), (10013, b'KEY_MODE_ERR'), (10014, b'KEY_ERR'), (-10000, b'NO_SUCH_FILE'), (10002, b'LOGIN_TIMEOUT_ERR'), (10034, b'JOB_TIMEOUT_ERR'), (-14, b'SCRIPT_TIMEOUT_ERR'), (10032, b'UPLOAD_TIMEOUT_ERR'), (10035, b'P2P_TIMEOUT_ERR'), (10016, b'COMMON_ERROR'), (10015, b'UNEXPECT_RETURN'), (10012, b'CON_REFUSED'), (10003, b'WRONG_PASSWORD'), (10004, b'WRONG_PORT'), (10005, b'SSH_LOGIN_EXCP'), (10001, b'APP_EXCP'), (10031, b'FORCE_STOP'), (10006, b'PROXY_UNUSEABLE'), (10007, b'CELERY_TASK_EXCP'), (10010, b'AUTH_WAY_ERROR'), (999, b'STILL_RUNNING'), (-1, b'INSTALL_FAILED'), (-2, b'CHECK_OS_FAILED'), (-3, b'MODIFY_CONF_FAILED'), (-12, b'TELNET_FAILED'), (-4, b'CHECK_OS_FAILED'), (-13, b'ADD_IPTABLES_FAILED'), (-5, b'COPY_FAILED'), (-6, b'TAR_XF_FAILED'), (-7, b'TELNET_SERVER_PORT_FAILED'), (-8, b'EXE_FILE_NOT_EXISTS'), (-9, b'COPY_TEMPLATE_FAILED'), (-10, b'CHECK_RUNMODE_FAILED'), (-11, b'CHECK_IPV6_FAILED'), (-16, b'NO_ROUTE_TO_HOST')])),
                ('type', models.SmallIntegerField(default=0, verbose_name='\u673a\u5668\u7c7b\u578b', choices=[(0, b'proxy'), (1, b'agent')])),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u5b89\u88c5\u5931\u8d25\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u5b89\u88c5\u5931\u8d25\u7edf\u8ba1\u8868',
                'verbose_name_plural': '\u5b89\u88c5\u5931\u8d25\u7edf\u8ba1\u8868',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyWeatherByCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.IntegerField()),
                ('boston_temp', models.DecimalField(max_digits=5, decimal_places=1)),
                ('houston_temp', models.DecimalField(max_digits=5, decimal_places=1)),
                ('new_york_temp', models.DecimalField(max_digits=5, decimal_places=1)),
                ('san_franciso_temp', models.DecimalField(max_digits=5, decimal_places=1)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyWeatherSeattle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.IntegerField()),
                ('seattle_temp', models.DecimalField(max_digits=5, decimal_places=1)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SalesHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sale_date', models.DateField()),
                ('sale_qty', models.IntegerField()),
                ('price', models.DecimalField(max_digits=5, decimal_places=2)),
                ('book', models.ForeignKey(to='chartapp.Book')),
                ('bookstore', models.ForeignKey(to='chartapp.BookStore')),
            ],
        ),
        migrations.AddField(
            model_name='bookstore',
            name='city',
            field=models.ForeignKey(to='chartapp.City'),
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='chartapp.Genre', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='chartapp.Publisher', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='related',
            field=models.ManyToManyField(related_name='_book_related_+', to='chartapp.Book', db_column=b'related', blank=True),
        ),
    ]
