"""
1.集成配置类
2.集成sqlalchemy
3.集成redis，测试redis是否能写入
4.集成CSRFProtect
5.session保存到redis的配置
6.集成flask_script
7.集成flask_migrate
"""
import logging

from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

app = create_app("develop")
# 6.集成flask_script
manager = Manager(app)
# 7.集成数据库迁移flask_migrate,在flask中对数据库迁移
Migrate(app, db)
manager.add_command("db",MigrateCommand)


@app.route("/")
def index():
    logging.debug("debug")
    logging.error("error")
    logging.warning("warning")
    logging.info("info")
    logging.fatal("fatal")

    current_app.logger.debug("我是flask中的debug哈哈")

    return "index"


if __name__ == '__main__':
    manager.run()