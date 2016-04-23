# -*- coding: utf-8 -*-
from django.contrib import admin
from djcelery.models import TaskMeta, TaskSetMeta
from chat.models import Item

# Register your models here.
class TaskMetaAdmin(admin.ModelAdmin):
    # fields = ('task_id', 'status', 'result', 'traceback')
    list_display = ['task_id', 'status', 'result', 'date_done', 'traceback']
    list_filter = ['date_done', 'status', 'result']
    search_fields = ('task_id', 'status', 'result')

class ItemAdmin(admin.ModelAdmin):
    list_display = ['text', 'date_posted']


from kombu.transport.django import models as kombu_models
admin.site.register(kombu_models.Message)

admin.site.register(TaskMeta, TaskMetaAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(TaskSetMeta)
