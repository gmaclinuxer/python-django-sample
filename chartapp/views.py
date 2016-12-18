# -*- coding: utf-8 -*-

import datetime
import random

from chartit import Chart, DataPool, PivotChart, PivotDataPool
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, render_to_response

# Create your views here.
from chartapp.models import (ERR_DICT, STILL_RUNNING, SUCCESS, UNKNOWN,
                             FailedStat, MonthlyWeatherByCity, SalesHistory)
from config import settings


def test(request):
    MonthlyWeatherByCity.objects.all().delete()
    for x in range(20):
        MonthlyWeatherByCity.objects.create(
            month=random.randrange(1, 13),
            boston_temp=random.randint(10, 30),
            houston_temp=random.randint(10, 30),
            new_york_temp=random.randint(10, 30),
            san_franciso_temp=random.randint(10, 30)
        )

    ds = DataPool(
        series=
        [{'options': {
            'source': MonthlyWeatherByCity.objects.all()},
            'terms': [
                'month',
                'boston_temp',
                'houston_temp']}
        ])

    def monthname(month_num):
        names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        return names[month_num]

    try:
        cht = Chart(
            datasource=ds,
            series_options=
            [{'options': {
                'type': 'line'},
                'terms': {
                    'month': [
                        'boston_temp']
                }},
                {'options': {
                    'type': 'pie',
                    'center': [150, 100],
                    'size': '50%'},
                    'terms': {
                        'month': [
                            'houston_temp']
                    }}],
            chart_options=
            {'title': {
                'text': 'Weather Data of Boston (line) and Houston (pie)'}},
            x_sortf_mapf_mts=[(None, monthname, False),
                              (None, monthname, False)])
    except Exception as e:
        raise e
    return render_to_response('index.html', {'weatherchart': cht, 'STATIC_URL': settings.STATIC_URL})


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
                    'text': 'Month number'}}})
    # Step 3: Send the chart object to the template.
    return render_to_response('index.html', {'weatherchart': cht, 'STATIC_URL': settings.STATIC_URL})


def pie(request, top_n=10):
    def err_map(item):
        return ERR_DICT.get(item, 'UNKNOWN')

    FailedStat.objects.all().delete()
    FailedStat.random(500)
    # Step 2: Create the Chart object
    ds = DataPool(
        series=[
            {
                'options': {
                    'source': FailedStat.objects.exclude(err_code__in=[
                        UNKNOWN,
                        SUCCESS,
                        STILL_RUNNING
                    ]).values('err_code').annotate(err_count=Count('err_code')).order_by('-err_count')[:top_n],
                },
                'terms': [
                    'err_code',
                    'err_count',
                ]
            },
        ],
    )

    cht = Chart(
        datasource=ds,
        series_options=[
            {
                'options': {
                    'type': 'pie',
                },
                'terms': {
                    'err_code': ['err_count']
                }
            },
        ],
        chart_options=
        {
            'chart': {
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
                },
            ],
        },
        x_sortf_mapf_mts=(None, err_map, True)
    )

    # Step 3: Send the chart object to the template.
    return render_to_response('index.html', {
        'weatherchart': cht,
        'STATIC_URL': settings.STATIC_URL
    })


def create_err_stat_chart(itype, top_n):
    def err_trans(item):
        return (ERR_DICT.get(int(item[0]), 'UNKNOWN'),)

    ds = PivotDataPool(
        series=[
            {
                'options': {
                    'source': FailedStat.objects.exclude(err_code__in=[
                        UNKNOWN,
                        SUCCESS,
                        STILL_RUNNING
                    ]),
                    'pointPlacement': 'on',
                    'categories': 'err_code',
                    # 'legend_by': 'err_code'
                },
                'terms': {
                    'err_stat': Count('err_code'),
                }
            },
        ],
        top_n=int(top_n),
        top_n_term='err_stat',
        pareto_term='err_stat',
        sortf_mapf_mts=(None, err_trans, True)
    )

    # polar mode
    if itype == 'polar':
        chart_options = {
            'chart': {
                'polar': True,
                'height': 600
            },
            'title': {
                'text': u'Agent安装错误码统计图 - %s' % datetime.datetime.now().strftime('%Y-%m-%d')},
            'xAxis': {
                'title': {
                    'text': ''
                }
            },
            'yAxis': [
                {
                    'title': {
                        'text': ''
                    },
                },
            ],
            'tooltip': {
                'shared': True
            },
            'credits': {
                'enabled': False,
                # 'text': 'agent-setup',
                # 'href': 'http://agent-setup.qcloud.com/'
            }
        }
    else:
        chart_options = {
            'chart': {
                'height': 600
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
            ],
            'tooltip': {
                'shared': True
            },
            'credits': {
                'enabled': False,
                # 'text': 'agent-setup',
                # 'href': 'http://agent-setup.qcloud.com/'
            }
        }
    cht = PivotChart(
        datasource=ds,
        series_options=[
            {
                'options': {
                    'type': 'column',
                },
                'terms': [
                    'err_stat',
                ]
            },
        ],
        chart_options=chart_options
    )

    return cht


def create_err_stat_pie(top_n):
    def err_map(item):
        return ERR_DICT.get(item, 'UNKNOWN')

    # Step 2: Create the Chart object
    ds = DataPool(
        series=[
            {
                'options': {
                    'source': FailedStat.objects.exclude(err_code__in=[
                        UNKNOWN,
                        SUCCESS,
                        STILL_RUNNING
                    ]).values('err_code').annotate(err_count=Count('err_code')).order_by('-err_count')[:top_n],
                },
                'terms': [
                    'err_code',
                    'err_count',
                ]
            },
        ],
    )

    cht = Chart(
        datasource=ds,
        series_options=[
            {
                'options': {
                    'type': 'pie',
                },
                'terms': {
                    'err_code': ['err_count']
                }
            },
        ],
        chart_options=
        {
            'chart': {
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
                },
            ],
        },
        x_sortf_mapf_mts=(None, err_map, True)
    )
    return cht

def fail_state(request, top_n):
    FailedStat.objects.all().delete()
    FailedStat.random(500)
    cht_polar = create_err_stat_chart('polar', top_n)
    cht_column = create_err_stat_chart('column', top_n)
    cht_pie = create_err_stat_pie(top_n)
    return render(request, 'chart.html', {
        'chart_list': [cht_column, cht_polar, cht_pie],
        'STATIC_URL': settings.STATIC_URL
    })
