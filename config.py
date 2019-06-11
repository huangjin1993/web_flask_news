import logging

from redis import StrictRedis


class Config(object):
    SECRET_KEY = 'ABCD'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/flask_news"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USER_SIGNER = True

    SESSION_PERMANENT = False
    PERMANENT_LIFETIME = 86400 * 2

    # 设置数据库的默认提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


# 使用面向对象的继承，继承Config，不同环境创建不同的配置
class DevelopConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.ERROR


class TestingConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.WARNING


# 使用字典封装每个类
config = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "testing": TestingConfig
    }