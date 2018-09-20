# -*- coding:utf-8 -*-
import logging

__author__ = 'ChenJiaBao'
__date__ = '2018/9/19 17:56'
from flask import session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

# 通过配置指定的名字创建对应配置的app
app = create_app('development')
manager = Manager(app)

# 将app和db关连
Migrate(app, db)
# 将数据库迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    # session['name'] = 'laowang'
    logging.debug('测试debug')
    logging.warning('测试warning')
    logging.error('测试error')
    return 'index'


if __name__ == '__main__':
    manager.run()
