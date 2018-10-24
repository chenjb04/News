# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 15:02'
from . import index_blu
from flask import render_template, current_app, session
from info.models import User, News


@index_blu.route('/')
def index():
    """
    首页
    :return:
    """
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    data = {
        'user': user.to_dict() if user else None
    }

    # 右侧排行数据
    news_list = News.query.order_by(News.clicks.desc()).limit(6)
    return render_template('news/index.html', data=data, news_list=news_list)


@index_blu.route('/favicon.ico')
def favicon():
    """加载网站小图标"""
    return current_app.send_static_file('news/favicon.ico')