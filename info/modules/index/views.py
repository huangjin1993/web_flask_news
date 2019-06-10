from flask import render_template, send_file, redirect, current_app, session

from info import redis_store, constants
from info.models import User, News
from info.modules.index import index_blu


@index_blu.route("/")
def index():
    """
    需求:首页右上角实现
    当进入到首页,判断是否登录,如果登录,将用户的信息查出来渲染index.html
    :return:
    """
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 显示新闻排行
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    clicks_news_li = [news_obj.to_basic_dict() for news_obj in clicks_news]




    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li
    }

    return render_template("news/index.html",data = data)


@index_blu.route("/favicon.ico")
def favicon():
    # 1.重定向(一般不用)
    # return redirect("/static/news/favicon.ico")
    # 2.
    return current_app.send_static_file("news/favicon.ico")
    # 3.
    # return send_file("/static/news/favicon.ico")