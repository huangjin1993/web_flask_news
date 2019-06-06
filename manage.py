"""
1.集成配置类
2.集成sqlalchemy
3.集成redis，测试redis是否能写入
4.集成CSRFProtect
5.session保存到redis的配置
6.集成flask_script
7.集成flask_migrate
"""


from flask import Flask, session
from  flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand



class Config(object):
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


app = Flask(__name__)
# 1.集成配置类
app.config.from_object(Config)
# 2.集成sqlalchemy
db = SQLAlchemy(app)
# 3.集成redis
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# 4.SCRFProtect,用来以后设置校验值
CSRFProtect(app)
# 5.集成flask_session
Session(app)
# 6.集成flask_script
manager = Manager(app)
# 7.集成数据库迁移flask_migrate,在flask中对数据库迁移
Migrate(app, db)
manager.add_command("db",MigrateCommand)


@app.route("/")
def index():
    session['name'] = "haha"
    return "index"


if __name__ == '__main__':
    manager.run()