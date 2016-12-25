# -*- coding: utf-8 -*-
"""
提供需要额外分析的函数和模块给line_profile
"""

from debug_toolbar_line_profiler import signals
from chartapp.models import FailedStat


def register_profile_views(sender, profiler, **kwargs):
    profiler.add_function(FailedStat.random)


signals.profiler_setup.connect(register_profile_views,
                               dispatch_uid='register_profile_views')