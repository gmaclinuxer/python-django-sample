# -*- coding: utf-8 -*-
import random


def sort_print(func, items=None):
    """ Create random data and sort """
    if items is None:
        items = [random.randint(-50, 100) for c in range(32)]
    print 'before sort use <%s>: %s' % (func.func_name, items)
    sorted_items = func(items)
    print 'before sort use <%s>: %s' % (func.func_name, sorted_items)


def bubble_sort(items):
    """ Implementation of bubble sort """
    len_items = len(items)
    # 第i大/小
    for i in range(len_items):
        # 从剩余的LEN-i中冒泡得到
        for j in range(len_items - 1 - i):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items

if __name__ == '__main__':
    sort_print(func=bubble_sort)
