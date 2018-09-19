# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/9/19 17:56'
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run(debug=True)
