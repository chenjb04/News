# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/31 20:13'
from flask import render_template, request, session, redirect, url_for, g, current_app, jsonify
from . import admin_blu
from info.models import User, News, Category
from info.utils.common import user_login_data
import time
import datetime
from info.utils.response_code import RET
from info.utils.image_storage import storage
from info.constants import QINIU_DOMIN_PREFIX
from info import db


@admin_blu.route('/login', methods=['GET', 'POST'])
def login():
    """
    后台登录
    :return:
    """
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.index'))
        return render_template('admin/login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='请填写完整内容')
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或者密码有误')
    except Exception as e:
        return render_template('admin/login.html', errmsg='未查询到用户信息')

    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    session['is_admin'] = user.is_admin
    return redirect(url_for('admin.index'))


@admin_blu.route('/logout')
def logout():
    """
    后台退出
    :return:
    """
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    session.pop('is_admin', None)
    return redirect(url_for('index.index'))


@admin_blu.route('/index')
@user_login_data
def index():
    """
    后台主页
    :return:
    """
    user = g.user

    return render_template('admin/index.html', user=user)


@admin_blu.route('/user_count')
def user_count():
    """
    后台用户数据显示
    :return:
    """
    total_count = 0
    mon_count = 0
    day_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > datetime.datetime.strptime(('%d-%02d-01' % (time.localtime().tm_year, time.localtime().tm_mon)), '%Y-%m-%d')).count()
    except Exception as e:
        current_app.logger.error(e)

    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > datetime.datetime.strptime(('%d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday  )), '%Y-%m-%d')).count()
    except Exception as e:
        current_app.logger.error(e)

    active_time = []
    active_count = []
    begin_today_date = datetime.datetime.strptime(('%d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)), '%Y-%m-%d')
    for i in range(0, 31):
        begin_date = begin_today_date - datetime.timedelta(days=i)
        end_date = begin_today_date - datetime.timedelta(days=i - 1)
        count = User.query.filter(User.is_admin == False, User.last_login    >= begin_date, User.last_login <= end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))
    active_time.reverse()
    active_count.reverse()
    data = {
        'total_count': total_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_count': active_count,
        'active_time': active_time
    }
    return render_template('admin/user_count.html', data=data)


@admin_blu.route('/user_list')
def user_list():
    """
    后台用户列表
    :return:
    """
    page = request.args.get('p', 1)
    page = int(page)
    pagination = User.query.filter(User.is_admin == False).paginate(page, 10, False)
    return render_template('admin/user_list.html', paginate=pagination)


@admin_blu.route('/news_review_list')
def news_review_list():
    """
    后台新闻审核列表
    :return:
    """
    page = request.args.get('p', 1)
    page = int(page)

    key_words = request.args.get('key_words', None)
    filters = [News.status != 0]
    if key_words:
        filters.append(News.title.contains(key_words))

    pagination = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    return render_template('admin/news_review.html', paginate=pagination)


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    """
    后台新闻审核详情
    :return:
    """
    news = News.query.filter(News.id == news_id).first()
    category = Category.query.filter(Category.id == news.category_id).first()
    return render_template('admin/news_review_detail.html', news=news, category=category)


@admin_blu.route('/news_review_doing', methods=["POST", 'GET'])
def news_review_doing():
    """
    新闻审核
    :return:
    """
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ('accept', 'reject'):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    news = News.query.get(news_id)
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="参数错误")
    if action == 'accept':
        news.status = 0
    else:
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.status = -1
        news.reason = reason
    return jsonify(errno=RET.OK, errmsg="ok")


@admin_blu.route('/news_edit_list')
def news_edit_list():
    """
    新闻编辑
    :return:
    """
    page = request.args.get('p', 1)
    page = int(page)
    key_words = request.args.get('key_words', None)
    filters = [News.status == 0]
    if key_words:
        filters.append(News.title.contains(key_words))

    pagination = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    return render_template('admin/news_edit.html', pagination=pagination)


@admin_blu.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    """
    后台新闻编辑详情
    :return:
    """

    if request.method == 'GET':
        news_id = request.args.get('news_id')
        news = News.query.filter(News.id == news_id).first()
        category = Category.query.all()
        return render_template('admin/news_edit_detail.html', news=news, category=category)
    else:
        title = request.form.get('title')
        digest = request.form.get('digest')
        content = request.form.get('content')
        index_image = request.files.get('index_image').read()
        category_id = request.form.get('category_id')
        if not all([title, content, digest, category_id]):
            return jsonify(errno=RET.PARAMERR, errmsg='请填写完整信息')
        news_id = request.form.get('news_id')
        news = News.query.filter(News.id == news_id).first()
        news.title = title
        news.digest = digest
        news.content = content
        key = storage(index_image)
        news.index_image_url = QINIU_DOMIN_PREFIX + key
        news.category_id = category_id
        return jsonify(errno=RET.OK, errmsg='ok')


@admin_blu.route('/news_category', methods=['POST', 'GET'])
def news_category():
    """
    后台新闻分类
    :return:
    """
    if request.method == 'GET':
        category = Category.query.all()
        return render_template("admin/news_type.html", category=category)
    category_name = request.json.get('name')
    category_id = request.json.get('id')
    if not category_name:
        return jsonify(errno=RET.PARAMERR, errmsg='请填写完整信息')
    if category_id:
        try:
            category_id = int(category_id)
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        if not category:
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        category.name = category_name
    else:
        category = Category()
        category.name = category_name
        db.session.add(category)
    return jsonify(errno=RET.OK, errmsg='ok')