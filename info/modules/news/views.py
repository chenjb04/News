# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/29 13:50'
from info.modules.news import news_blu
from flask import render_template, g, request, jsonify, current_app
from info.models import News, Comment, User, CommentLike
from info import constants, db
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

    comments = None
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    comment_like_ids = []
    if g.user:
        comment_ids = [comment.id for comment in comments]
        comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids), CommentLike.user_id == g.user.id).all()
        comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]

    comment_list = []
    for item in comments if comments else []:
        comment_dict = item.to_dict()
        comment_dict['is_like'] = False
        if item.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_list.append(comment_dict)

    return render_template('news/detail.html', news=news, data=data, news_list=news_list, total_comment=total_comment,
                           is_collected=is_collected,
                           comments=comment_list)


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


@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def comment_news():
    """
    评论新闻
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    news_id = request.json.get('news_id')
    comments = request.json.get('comment')
    parent_id = request.json.get('parent_id', )
    if not all([news_id, comments]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    comment = Comment()
    news = News.query.get(news_id)
    comment.news_id = news_id
    comment.user_id = user.id
    comment.content = comments
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    return jsonify(errno=RET.OK, errmsg='ok', data=comment.to_dict())


@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    """
    评论点赞
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询错误')

    if action == 'add':
        comment_likes = CommentLike()
        comment_likes.user_id = user.id
        comment_likes.comment_id = comment.id
        comment.like_count += 1
        db.session.add(comment_likes)
    else:
        remove_comment_like = CommentLike.query.filter(CommentLike.user_id == user.id, CommentLike.comment_id == comment.id).first()
        if remove_comment_like:
            db.session.delete(remove_comment_like)
            if comment.like_count > 0:
                comment.like_count -= 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg='操作成功')

