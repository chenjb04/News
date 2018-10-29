# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/29 14:58'
import functools
from flask import session, current_app, g
from info.models import User


def user_login_data(f):
    """
    装饰器实现用户登录状态数据
    :param f:
    :return:
    """
    @functools.wraps(f)
    def wrappers(*args, **kwargs):
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args, **kwargs)
    return wrappers
