from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config


app = Flask(__name__)
# 1.集成配置类
app.config.from_object(config["develop"])
# 2.集成sqlalchemy
db = SQLAlchemy(app)
# 3.集成redis
redis_store = StrictRedis(host=config["develop"].REDIS_HOST,port=config["develop"].REDIS_PORT)
# 4.SCRFProtect,用来以后设置校验值
CSRFProtect(app)
# 5.集成flask_session
Session(app)