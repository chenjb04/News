# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/22 13:50'
# 登录注册逻辑
from flask import Blueprint

passport_blu = Blueprint('passport', __name__, url_prefix='/passport')
from . import views