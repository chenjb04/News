# -*- coding:utf-8 -*-
from info import redis_store

__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 15:02'
from . import index_blu


@index_blu.route('/')
def index():
    redis_store.set('name', 'hahahhaha')
    return 'index'
