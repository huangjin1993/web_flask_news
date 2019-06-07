import random
import re

from flask import request, abort, current_app, make_response, jsonify
from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET



# 1.请求的URL是什么
# 2.请求的方式什么
# 3.参数的名字是什么
# 4.返回的参数和参数类型



@passport_blu.route("/sms_code",methods=["POST"])
def get_sms_code():
    # 1.接受的参数摸moble image_code, image_code_id
    dict_data = request.data
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 全局做个校验
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 2.校验参数 moble 正则
    if re.match(r"1[35678]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不正确")

    # 3.校验用户输入的验证码 和通过image_code_id查出来的验证码是否一致
    try:
        real_image_code = redis_store.get("ImageCodeId" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")
    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")
        
    # 4.先去定义一个随机的验证码
    sms_code_str = "%06d" % random.randint(0,999999)
    current_app.logger.info("短信验证码为%s") % sms_code_str

    # 5.调用云通讯发送验证码
    result = CCP().send_template_sms(mobile,[sms_code_str,5],1)
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")

    # 6.将验证码保存到redis
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败"
    # 7.返回给前段一个响应
    return jsonify(errno=RET.OK, errmsg="发送短信验证码OK"



@passport_blu.route("/image_code")
def get_image_code():
    # 1.接受参数
    image_code_id = request.args.get("imageCodeId")
    # 2.校验参数是否存在
    if not image_code_id:
        abort(404)
    # 3.生成验证码
    _, text, image = captcha.generate_captcha()
    current_app.logger.info("图片验证码为%s") % text
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


