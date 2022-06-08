from flask import session, redirect, url_for
from functools import wraps

import os


def login_required(func):
    '''登录验证装饰器'''
    @wraps(func)
    def inner(*args, **kwargs):
        if 0:
            user = session.get('status')
            if not user:
                return redirect(url_for('html_user_login'), 302)
        else:
            session['status'] = True
            session['username'] = 'admin'
            session['login_ip'] = '0.0.0.0'
        return func(*args, **kwargs)
    return inner


def message(code=0, msg='ok', **kwargs):
    """响应体数据格式"""
    data = {"code": code, "msg": msg}
    data.update(**kwargs)
    return data

