"""
1.集成配置类
2.集成sqlalchemy

"""


from flask import Flask
from  flask_sqlalchemy import SQLAlchemy


class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/flask_news'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app = Flask(__name__)
# 1.集成配置类
app.config.from_object(app)
# 2.集成sqlalchemy
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    app.run()