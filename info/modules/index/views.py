# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 15:02'
from . import index_blu
from flask import render_template, current_app


@index_blu.route('/')
def index():
    return render_template('news/index.html')


@index_blu.route('/favicon.ico')
def favicon():
    """加载网站小图标"""
    return current_app.send_static_file('news/favicon.ico')