#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
requests.packages.urllib3.disable_warnings()


def _sign(secret):
    timestamp = str(round(time.time() * 1000))
    hmac_code = hmac.new(secret.encode('utf-8'), '{}\n{}'.format(timestamp,
                         secret).encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_text(text, token, secret="", atMobiles=[], isAtAll=False):
    """
    发送消息到钉钉群
    :param text: 发送的文本消息
    :param token: 钉钉群机器人token
    :param secret: 钉钉群机器人secret,为关键字或IP限制时可为空
    :param atMobiles: 要at的人的手机号列表
    :param isAtAll: at全部，默认False
    """
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "msgtype": "text",
        "text": {
            "content": text
        },
        "at": {
            "atMobiles": atMobiles,
            "isAtAll": isAtAll},
    }
    if secret:
        timestamp, sign = _sign(secret)
        url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(
            token, timestamp, sign)
    else:
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(
            token)
    r = requests.post(url, json=data, headers=headers,verify=False)
    return r.json()
