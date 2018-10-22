# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 15:02'
from . import index_blu
from flask import render_template


@index_blu.route('/')
def index():
    return render_template('news/index.html')
