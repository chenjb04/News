# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/19 17:56'
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models
from info.models import User


# 通过配置指定的名字创建对应配置的app
app = create_app('development')
manager = Manager(app)

# 将app和db关连
Migrate(app, db)
# 将数据库迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    if not all([name, password]):
        print('参数错误')
    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)


if __name__ == '__main__':
    manager.run()
