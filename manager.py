# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/19 17:56'
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config

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

manager = Manager(app)

# 将app和db关连
Migrate(app, db)
# 将数据库迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session['name'] = 'laowang'
    return 'index'


if __name__ == '__main__':
    manager.run()
