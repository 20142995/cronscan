FROM ubuntu:18.04

ENV LANG C.UTF-8

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

RUN apt-get clean && apt-get update 

RUN apt-get install -y python3 python3-pip language-pack-zh-hans fontconfig git wget 

WORKDIR /app

ADD ./ /app

RUN pip3 install -r requirements.txt  -i  https://pypi.tuna.tsinghua.edu.cn/simple 

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
