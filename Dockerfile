FROM ubuntu:18.04

ENV LANG C.UTF-8

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

RUN apt-get clean && apt-get update 

RUN apt-get install -y python3 python3-pip language-pack-zh-hans fontconfig git wget \
  build-essential libsqlite3-dev libpng-dev libjpeg-dev libxft-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev

WORKDIR /app

ADD ./ /app

RUN pip3 install -r requirements.txt  -i  https://pypi.tuna.tsinghua.edu.cn/simple 

RUN sed -i "s/from flask._compat import text_type/from flask_script._compat import text_type/g" /usr/local/lib/python3.6/dist-packages/flask_script/__init__.py

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
