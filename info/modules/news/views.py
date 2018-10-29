# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/29 13:50'
from info.modules.news import news_blu
from flask import render_template, g, request, jsonify, current_app
from info.models import News, User
from info import constants
from info.utils.common import user_login_data
from info.utils.response_code import RET


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
    total_comment = news.comments.count()
    news.clicks += 1
    # 右侧排行数据
    news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True

    return render_template('news/detail.html', news=news, data=data, news_list=news_list, total_comment=total_comment, is_collected=is_collected)


@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def collect_news():
    """收藏新闻"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询错误')
    # 取消收藏
    if action == 'cancel_collect':
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        # 收藏
        if news not in user.collection_news:
            user.collection_news.append(news)
    return jsonify(errno=RET.OK, errmsg='收藏成功')


