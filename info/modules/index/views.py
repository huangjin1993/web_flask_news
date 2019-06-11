from flask import render_template, send_file, redirect, current_app, session, request, jsonify, g

from info import redis_store, constants
from info.models import User, News, Category
from info.modules.index import index_blu
from info.utils.common import user_login
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    cid = request.args.get("cid")
    page = request.args.get("page")
    per_page = request.args.get("per_page",10)

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()). \
            paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询错误")

    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_li = [news.to_basic_dict() for news in news_list]

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }
    return jsonify(errno=RET.OK,errmsg="OK",data = data)


@index_blu.route("/")
@user_login
def index():
    """
    需求:首页右上角实现
    当进入到首页,判断是否登录,如果登录,将用户的信息查出来渲染index.html
    :return:
    """
    user = g.user
    # 显示新闻排行
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    clicks_news_li = [news_obj.to_basic_dict() for news_obj in clicks_news]

    # 显示新闻分类
    categorys = []
    try:
        categorys = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
    categorys_li = [category.to_dict() for category in categorys]

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li,
        "categorys_li": categorys_li
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