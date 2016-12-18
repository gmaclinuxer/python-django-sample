# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


def home(request):
    return JsonResponse({'result': True, 'data': [], 'message': u'operate successfully.'})
