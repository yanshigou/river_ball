# -*- coding: utf-8 -*-

from django import template
register = template.Library()


@register.simple_tag
def getMyArr(arr, ind):
    return arr[ind] 
