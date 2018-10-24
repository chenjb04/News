# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 13:43'
from redis import StrictRedis
import logging


class Config(object):
    """项目的配置"""
    SECRET_KEY = 'zDJkOqA5xDugTzSaTEk5g/dGqIoZjuw+j9e/jBvTeizbko/CFQb5TZQHek2zUpvU'
    # mysql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = 123456
    # Session 配置
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True  # 开启session签名
    SESSION_PERMANENT = False  # 设置需要过期
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间为两天
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

    LOG_LEVEL = logging.DEBUG


class Development(Config):
    """开发环境下的配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    """单元测试环境配置"""
    DEBUG = True
    TESTING = True


config = {
    'development': Development,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
