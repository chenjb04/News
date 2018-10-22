# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/22 13:52'
from . import passport_blu
from flask import request, abort, current_app, make_response
from info import redis_store
from info import constants
from info.utils.captcha import captcha


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
    

