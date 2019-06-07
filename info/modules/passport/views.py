from flask import request, abort, current_app, make_response
from info import redis_store, constants
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route("/image_code")
def get_image_code():
    # 1.接受参数
    image_code_id = request.args.get("imageCodeId")
    # 2.校验参数是否存在
    if not image_code_id:
        abort(404)
    # 3.生成验证码
    _, text, image = captcha.generate_captcha()
    # 4.把生成的随机字符串以key value形式保存到redis
    try:
        redis_store.setex("ImageCodeId" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5.把验证图片返回给浏览器
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response


