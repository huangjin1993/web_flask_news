from flask import render_template, send_file, redirect, current_app

from info import redis_store
from info.modules.index import index_blu


@index_blu.route("/")
def index():

    return render_template("news/index.html")


@index_blu.route("/favicon.ico")
def favicon():
    # 1.重定向(一般不用)
    # return redirect("/static/news/favicon.ico")
    # 2.
    return current_app.send_static_file("news/favicon.ico")
    # 3.实现不了,方法估计有问题
    # return send_file("/static/news/favicon.ico")