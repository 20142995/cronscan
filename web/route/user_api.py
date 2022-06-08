import datetime
from flask import session, request
from flask_restful import reqparse, Resource
from werkzeug.security import check_password_hash
from web import app
from web.models import User
from web.utils.common import message


class UserLogin(Resource):
    '''登录'''

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("username", type=str,
                                 required=True, location='json')
        self.parser.add_argument("password", type=str,
                                 required=True, location='json')
        self.parser.add_argument(
            "captcha", type=str, required=True, location='json')
        self.parser.add_argument("rememberMe", type=bool, location='json')

    def post(self):
        '''登录'''
        args = self.parser.parse_args()
        key_username = args.username
        key_password = args.password
        key_vercode = args.captcha
        key_remember = args.rememberMe
        # 获取客户端IP地址
        try:
            login_ip = request.headers['X-Forwarded-For'].split(',')[0]
        except:
            login_ip = request.remote_addr
        # 处理验证码
        if 'code' not in session:
            return message(202, '验证码错误')
        if session.get('code').lower() != key_vercode.lower():
            session.pop('code')
            return message(202, '验证码错误')
        session.pop('code')
        # 若不存在此用户
        user_query = User.query.filter(User.username == key_username).first()
        if not user_query:
            return message(201, '')
        # 进行密码校验
        if check_password_hash(user_query.password, key_password):
            session['status'] = True
            session['username'] = key_username
            session['login_ip'] = login_ip
            if key_remember:
                session.permanent = True
                app.permanent_session_lifetime = datetime.timedelta(weeks=7)
            return message(200, 'ok')
        else:
            return message(201, '')
