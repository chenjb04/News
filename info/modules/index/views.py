# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 15:02'
from . import index_blu
from flask import render_template, current_app, session, request, jsonify, g
from info.models import User, News, Category
from info import constants
from info.utils.response_code import RET
from info.utils.common import user_login_data


@index_blu.route('/')
@user_login_data
def index():
    """
    首页
    :return:
    """
    user = g.user
    data = {
        'user': user.to_dict() if user else None
    }

    # 右侧排行数据
    news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    # 查询分类数据
    categories = Category.query.all()

    return render_template('news/index.html', data=data, news_list=news_list, categories=categories)


@index_blu.route('/favicon.ico')
def favicon():
    """加载网站小图标"""
    return current_app.send_static_file('news/favicon.ico')


@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    """
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)
    try:
        page_data = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        total_page = page_data.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
    news_data = []
    for news in page_data.items:
        news_data.append(news.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg='ok', news_data=news_data, total_page=total_page)

