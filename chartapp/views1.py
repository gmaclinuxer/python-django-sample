# -*- coding: utf-8 -*-

import datetime
import random

from chartit import Chart, DataPool, PivotChart, PivotDataPool
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, render_to_response

# Create your views here.
from chartapp.models import (ERR_DICT, STILL_RUNNING, SUCCESS, UNKNOWN,
                             FailedStat, MonthlyWeatherByCity)
from config import settings


def err_trans(item):
    return (ERR_DICT[int(item[0])],)


def pivot(request):
    FailedStat.objects.all().delete()
    FailedStat.random(500)
    # Step 2: Create the Chart object
    ds = PivotDataPool(
        series=
        [
            {
                'options': {
                    'source': FailedStat.objects.exclude(err_code__in=[
                        UNKNOWN,
                        SUCCESS,
                        STILL_RUNNING
                    ]),
                    'categories': ['err_code'],
                    # 'legend_by': 'err_code'
                },
                'terms': {
                    'err_stat': Count('err_code'),
                }
            },
            # {
            #     'options': {
            #         'source': FailedStat.objects.exclude(err_code__in=[
            #             UNKNOWN,
            #             SUCCESS,
            #             STILL_RUNNING
            #         ]),
            #         'categories': 'type',
            #         # 'legend_by': 'err_code'
            #     },
            #     'terms': {
            #         'err_count': Count('type')
            #     }
            # }
        ],
        top_n=25,
        top_n_term='err_stat',
        pareto_term='err_stat',
        # sortf_mapf_mts=(None, err_trans, True)
    )

    cht = PivotChart(
        datasource=ds,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    # 'type': 'line',
                },
                'terms': [
                    'err_stat',
                    # {'err_count': {
                    #     'type': 'pie',
                    #     'yAxis': 1}}
                ]
            },
        ],
        chart_options=
        {
            'chart': {
                # 'polar': True,
                # 'type': 'line',
                'height': 600,
            },
            'title': {
                'text': u'Agent安装错误码统计图 - %s' % datetime.datetime.now().strftime('%Y-%m-%d')},
            'xAxis': {
                'title': {
                    'text': u'错误码'
                }
            },
            'yAxis': [
                {
                    'title': {
                        'text': u'错误次数(次)'
                    },
                    'gridLineInterpolation': 'polygon',
                },
                {'opposite': True}
            ],
            'tooltip': {
                'shared': True
            },
            'credits': {
                # 'enabled': False,
                'text': 'agent-setup',
                'href': 'http://agent-setup.qcloud.com/'
            }
        },
    )

    # Step 3: Send the chart object to the template.
    return render_to_response('index.html', {
        'weatherchart': cht,
        'STATIC_URL': settings.STATIC_URL
    })


def index(request):
    MonthlyWeatherByCity.objects.all().delete()
    for x in range(20):
        MonthlyWeatherByCity.objects.create(
            month=x,
            boston_temp=random.randint(10, 30),
            houston_temp=random.randint(10, 30),
            new_york_temp=random.randint(10, 30),
            san_franciso_temp=random.randint(10, 30)
        )
    # Step 1: Create a DataPool with the data we want to retrieve.
    weatherdata = \
        DataPool(
            series=
            [{'options': {
                'source': MonthlyWeatherByCity.objects.all()},
                'terms': [
                    'month',
                    'san_franciso_temp',
                    'new_york_temp',
                    'houston_temp',
                    'boston_temp']}
            ])

    # Step 2: Create the Chart object
    cht = Chart(
        datasource=weatherdata,
        series_options=
        [{'options': {
            'type': 'column',
            'stacking': False},
            'terms': {
                'month': [
                    'boston_temp',
                    'houston_temp', ]
            }},
            {'options': {
                'type': 'line',
                'stacking': False},
                'terms': {
                    'month': [
                        'new_york_temp',
                        'san_franciso_temp']
                }}],
        chart_options=
        {'title': {
            'text': u'支持中文吗'},
            'xAxis': {
                'title': {
                    'text': 'Month number'}}},
        x_sortf_mapf_mts=(None, err_trans, False)
    )
    # Step 3: Send the chart object to the template.
    return render_to_response('index.html', {'weatherchart': cht, 'STATIC_URL': settings.STATIC_URL})
