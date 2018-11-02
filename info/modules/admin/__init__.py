# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/31 20:12'
from flask import Blueprint, session, redirect, url_for, request

admin_blu = Blueprint('admin', __name__, url_prefix='/admin')
from . import views


@admin_blu.before_request
def check_admin():
    """
    校验
    :return:
    """
    is_admin = session.get('is_admin', False)
    if not is_admin and not request.url.endswith(url_for('admin.login')):
        return redirect(url_for('index.index'))