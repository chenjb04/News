# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/29 13:49'
from flask import Blueprint

news_blu = Blueprint('news', __name__, url_prefix='/news')

from . import views