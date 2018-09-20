# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 13:48'
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化数据库, 通过app初始化
    db.init_app(app)

    # 初始化redis存储对象
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT,
                              password=config[config_name].REDIS_PASSWORD)

    # 开启csrf
    CSRFProtect(app)

    # 设置session保存位置
    Session(app)
    return app
