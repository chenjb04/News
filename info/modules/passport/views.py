# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/22 13:52'
from . import passport_blu
from flask import request, abort, current_app, make_response, jsonify, session, redirect, url_for
from info import redis_store, db
from info import constants
from info.utils.captcha import captcha
from info.utils.response_code import RET
import re
import random
from info.utils.yuntongxun.sms import CCP
from info.models import User
import datetime


@passport_blu.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    短信验证码
    """
    params_dict = request.json
    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id = params_dict.get('image_code_id')
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if not re.match('^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\\d{8}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug('短信验证码内容是:%s' % sms_code_str)
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES], 1)
    print(result)
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    try:
        redis_store.set('SMS_'+mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存错误")
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route('/image_code')
def get_image_code():
    """
    生成图片验证码并且返回
    :return:
    """
    image_code_id = request.args.get('imageCodeId', None)
    if not image_code_id:
        return abort(403)
    name, text, image = captcha.captcha.generate_captcha()
    try:
        redis_store.set("ImageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.debug(e)
        abort(500)
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册
    """
    param_dict = request.json
    mobile = param_dict.get('mobile')
    smscode = param_dict.get('smscode')
    password = param_dict.get('password')
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if not re.match('^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\\d{8}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")
    try:
        real_sms_code = redis_store.get('SMS_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询失败')
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg='验证码输入错误')
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.last_login = datetime.datetime.now()
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库存储错误")
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    return jsonify(errno=RET.OK, errmsg='注册成功')


@passport_blu.route('/login', methods=['POST'])
def login():
    """
    登录
    """
    params_dict = request.json
    mobile = params_dict.get('mobile')
    password = params_dict.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if not re.match('^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\\d{8}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")
    try:
        user = User.query.filter_by(mobile=mobile).first()
        if user is None:
            return jsonify(errno=RET.NODATA, errmsg="用户不存在")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg='密码有误！')
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    user.last_login = datetime.datetime.now()
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='登录成功')


@passport_blu.route('/logout')
def logout():
    """
    退出
    """
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    return redirect(url_for('index.index'))




