# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/19 17:56'
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session


class Config(object):
    """项目的配置"""
    DEBUG = True
    SECRET_KEY = 'zDJkOqA5xDugTzSaTEk5g/dGqIoZjuw+j9e/jBvTeizbko/CFQb5TZQHek2zUpvU'
    # mysql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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


app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

# 初始化redis存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PASSWORD)

# 开启csrf
CSRFProtect(app)

# 设置session保存位置
Session(app)


@app.route('/')
def index():
    session['name'] = 'laowang'
    return 'index'


if __name__ == '__main__':
    app.run()
