import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


@passport_blu.route("/login",methods=["POST"])
def login():
    """
    1.接受参数
    2.校验参数,手机号格式是否正确
    3.保持用户登录状态
    4.设置用户登录时间
    5.返回响应
    :return:
    """
    dict_data = request.json
    mobile = dict_data.get("mobile")
    passport = dict_data.get("passport")

    if not all([mobile,passport]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不正确")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询错误")
    if not user:
        return jsonify(errno=RET.NODATA,errmsg="用户未注册")

    if not user.check_passowrd(passport):
        return jsonify(errno=RET.DATAERR,errmsg="密码错误")

    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据保存失败")

    session["user_id"] = user.id
    return jsonify(errno=RET.OK,errrmsg="登录成功")


@passport_blu.route("/register",methods=["POST"])
def register():
    """
    1.接受到的参数
    2.整体校验
    3.手机号格式验证
    4.从redis中取出短信验证码
    5.和用户输入的验证码对比
    6.初始化User添加数据
    7.session保持用户登录状态
    8.返回响应
    :return:
    """
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不正确")

    try:
        real_sms_code = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询短信验证码错误")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="duan信验证码过期")

    if smscode != real_sms_code:
        return jsonify(erron=RET.DATAERR,errmsg="短信验证码错误")

    # 核心逻辑
    user = User()
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库保存失败")

    # 设置用户登录状态
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 1.请求的URL是什么
# 2.请求的方式什么
# 3.参数的名字是什么
# 4.返回的参数和参数类型
@passport_blu.route("/sms_code",methods=["POST"])
def get_sms_code():
    # 1.接受的参数摸moble image_code, image_code_id
    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    # 全局做个校验
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    # 2.校验参数 moble 正则
    if not re.match(r"1[35678]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不正确")
    # 3.校验用户输入的验证码 和通过image_code_id查出来的验证码是否一致
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")
    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")
    # 4.先去定义一个随机的验证码
    sms_code_str = "%06d" % random.randint(0,999999)
    current_app.logger.info("短信验证码为%s" % sms_code_str)
    # 5.调用云通讯发送验证码
    # result = CCP().send_template_sms(mobile,[sms_code_str,5],1)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")

    # 6.将验证码保存到redis
    try:
        redis_store.setex("SMS_" + mobile, constants.IMAGE_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败")
    # 7.返回给前段一个响应
    return jsonify(errno=RET.OK, errmsg="发送短信验证码OK")


@passport_blu.route("/image_code")
def get_image_code():
    # 1.接受参数
    image_code_id = request.args.get("imageCodeId_")
    # 2.校验参数是否存在
    if not image_code_id:
        print("*"*89)
        abort(404)
    # 3.生成验证码
    _, text, image = captcha.generate_captcha()
    current_app.logger.info("图片验证码为%s" % text)
    # 4.把生成的随机字符串以key value形式保存到redis
    try:
        redis_store.setex("ImageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5.把验证图片返回给浏览器
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response
