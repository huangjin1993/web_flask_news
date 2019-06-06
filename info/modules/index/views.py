from info import redis_store
from info.modules.index import index_blu


@index_blu.route("/")
def index():
    redis_store.set("name","laozhang")
    return "index"