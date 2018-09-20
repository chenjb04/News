# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 15:01'
from flask import Blueprint

# 创建蓝图对象
index_blu = Blueprint('index', __name__)

from . import views
