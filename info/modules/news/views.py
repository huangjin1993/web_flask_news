from flask import render_template, current_app, g, abort

from info import constants
from info.models import News
from info.modules.news import news_blu
from info.utils.common import user_login


@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页面渲染
    :param news_id:
    :return:
    """
    user = g.user
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    clicks_news_li = [news_obj.to_basic_dict() for news_obj in clicks_news]

    # 显示具体的新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)
    print(news.clicks)
    news.clicks += 1
    print(news.clicks)
    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li,
        "news": news.to_dict()
    }

    return render_template("news/detail.html",data=data)