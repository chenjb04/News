# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/30 16:54'
from flask import Blueprint

profile_blu = Blueprint('profile', __name__, url_prefix='/user')

from . import views