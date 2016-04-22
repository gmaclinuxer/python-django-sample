# -*- coding: utf-8 -*-
from django.db import models

class Item(models.Model):
    text = models.TextField(blank=False, null=False)
    date_posted = models.DateField(auto_now=True)

    def __unicode__(self):
        return u'%s-%s' % (self.text, self.date_posted)

    class Meta:
        verbose_name = u'评论记录'
        verbose_name_plural = u'评论记录'