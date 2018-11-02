# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/30 16:55'
from . import profile_blu
from flask import render_template, g, redirect, request, jsonify, current_app
from info.utils.common import user_login_data
from info.utils.response_code import RET
from info.utils.image_storage import storage
from info.constants import QINIU_DOMIN_PREFIX
from info.models import Category, News, User
from info import db


@profile_blu.route('/info')
@user_login_data
def user_info():
    """
    用户中心
    :return:
    """
    user = g.user
    if not user:
        return redirect('/')
    data = {
        'user': user.to_dict()
    }
    return render_template('news/user.html', data=data)


@profile_blu.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """
    用户基本资料
    :return:
    """
    if request.method == 'GET':
        user = g.user
        if not user:
            return redirect('/')
        data = {
            'user': user
        }
        return render_template('news/user_base_info.html', data=data)
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='请全部填写')
    if gender not in ('MAN', 'WOMAN'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    user = g.user
    user.gender = gender
    user.nick_name = nick_name
    user.signature = signature
    return jsonify(errno=RET.OK, errmsg='操作成功')


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    """
    头像修改
    :return:
    """
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user": user.to_dict()})

    # 如果是POST表示修改头像
    # 1. 取到上传的图片
    try:
        avatar = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 2. 上传头像
    try:
        # 使用自已封装的storage方法去进行图片上传
        key = storage(avatar)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    # 3. 保存头像地址
    user.avatar_url = key
    return jsonify(errno=RET.OK, errmsg="OK", data={"avatar_url": QINIU_DOMIN_PREFIX + key})


@profile_blu.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    """
    修改密码
    :return:
    """
    if request.method == 'GET':
        return render_template("news/user_pass_info.html")
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    repeat_new_password = request.json.get('repeat_new_password')
    if not all([old_password, new_password, repeat_new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="请填写完整内容")
    user = g.user
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg='旧密码错误')
    if new_password != repeat_new_password:
        return jsonify(errno=RET.PWDERR, errmsg='两次密码不一致')
    user.password = new_password
    return jsonify(errno=RET.OK, errmsg='ok')


@profile_blu.route('/collection', methods=['GET', 'POST'])
@user_login_data
def user_collection():
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    paginate = user.collection_news.paginate(page, 10, False)
    current_page = paginate.page
    total_page = paginate.pages
    return render_template('news/user_collection.html', paginate=paginate, current_page=current_page, total_page=total_page)


@profile_blu.route('/release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    """
    新闻发布
    :return:
    """
    if request.method == "GET":
        categories = Category.query.all()
        categories.pop(0)
        return render_template('news/user_news_release.html', categories=categories)
    title = request.form.get('title')
    source = "个人发布"
    digest = request.form.get('digest')
    content = request.form.get('content')
    index_image = request.files.get('index_image').read()
    category_id = request.form.get('category_id')
    if not all([title, source, content, index_image, digest, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='请填写完整信息')
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    key = storage(index_image)
    news.index_image_url = QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据存储错误')
    return jsonify(errno=RET.OK, errmsg='ok')


@profile_blu.route('/user_news_list')
@user_login_data
def user_news_list():
    """
    新闻列表
    :return:
    """
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    paginate = News.query.filter(News.user_id == user.id).paginate(page, 3, False)
    current_page = paginate.page
    total_page = paginate.pages
    return render_template('news/user_news_list.html', paginate=paginate, current_page=current_page, total_page=total_page)


@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    """
    用户收藏
    :return:
    """
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    pagination = user.followed.paginate(page, 4, False)
    total_news_count = user.news_list.filter(News.status == 0).count()
    followers_count = user.followers.count()
    return render_template('news/user_follow.html', paginate=pagination,
                           total_news_count=total_news_count,
                           followers_count=followers_count
                           )


@profile_blu.route('/other')
@user_login_data
def other():
    """
    其他用户
    :return:
    """
    user = g.user
    data = {
        'user': user
    }
    other_user_id = request.args.get('user_id')
    other_user = User.query.get(other_user_id)
    is_followed = False
    if g.user:
        if other_user.followers.filter(User.id == user.id).count() > 0:
            is_followed = True
    return render_template('news/other.html', data=data, other_user=other_user, is_followed=is_followed)


@profile_blu.route('/other_news_list')
def other_news_list():
    """
    其他用户新闻列表
    :return:
    """
    # 获取页数
    p = request.args.get("p", 1)
    user_id = request.args.get("user_id")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not all([p, user_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    try:
        paginate = News.query.filter(News.user_id == user.id, News.status == 0).paginate(p, 1, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())
    data = {"news_list": news_dict_li, "total_page": total_page, "current_page": current_page}
    return jsonify(errno=RET.OK, errmsg="OK", data=data)