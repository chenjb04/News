# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/20 13:48'
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler
from info.modules.index import index_blu

db = SQLAlchemy()


def setup_log(congfig_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[congfig_name].LOG_LEVEL)
    # 创建日志记录器，指明日志的保存路径，每个日志文件的最大大小，保存的日志文件个数上限
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式，日志等级，输入日志信息的文件名，行数日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚才创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局日志工具对象，添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # 设置日志
    setup_log(config_name)
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

    # 注册蓝图
    app.register_blueprint(index_blu)
    return app
