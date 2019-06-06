"""
1.集成配置类
2.集成sqlalchemy
3.集成redis，测试redis是否能写入
4.集成CSRFProtect
"""


from flask import Flask
from  flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect


class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/flask_news'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


app = Flask(__name__)
# 1.集成配置类
app.config.from_object(app)
# 2.集成sqlalchemy
db = SQLAlchemy(app)
# 3.集成redis
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# 4.SCRFProtect,用来以后设置校验值
CSRFProtect(app)


@app.route("/")
def index():
    redis_store.set('name',"test")
    return "index"


if __name__ == '__main__':
    app.run()