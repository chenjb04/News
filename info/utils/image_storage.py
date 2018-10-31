# -*- coding:utf-8 -*-
__author__ = 'ChenJiaBao'
__date__ = '2018/10/30 18:58'
from qiniu import Auth, put_data

access_key = 'Yv0-lK-pI3SyHVUY7zOiIhVT_DDcY87kQL57mryt'
secret_key = 'ohWeplIfvaXz2ylViHND9Fqaf5xVDl0jT081se8C'
bucket_name = 'chenjb'


def storage(data):
    """
    七牛云图片上传
    :param data:
    :return:
    """
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
    except Exception as e:
        raise e
    if info.status_code != 200:
        raise Exception('上传图像失败')
    return ret['key']


if __name__ == '__main__':
    with open(r"D:\file\LearnOnline\media\teacher\2018\05\aobama.png", "rb") as f:
        storage(f.read())

