# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/29 13:50'
from info.modules.news import news_blu
from flask import render_template, g
from info.models import News, User
from info import constants
from info.utils.common import user_login_data


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情页
    """
    user = g.user
    data = {
        'user': user.to_dict() if user else None
    }
    news = News.query.filter(News.id == news_id).first()
    # 右侧排行数据
    news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    return render_template('news/detail.html', news=news, data=data, news_list=news_list)


