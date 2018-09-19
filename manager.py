# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/19 17:56'
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """项目的配置"""
    DEBUG = True
    # mysql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()
