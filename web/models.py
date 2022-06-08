from sqlalchemy import func
from web import db


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, comment='用户名')
    password = db.Column(db.TEXT(65535), comment='密码')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')

class Target(db.Model):
    __tablename__ = 'Target'
    id = db.Column(db.Integer, primary_key=True)
    target_group = db.Column(db.String(100), comment='目标分组名')
    target_type = db.Column(db.String(100), comment='目标类型')
    target = db.Column(db.TEXT(65535), comment='目标资产')
    note = db.Column(db.TEXT(65535), comment='备注')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')

class Task(db.Model):
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), comment='目标分组名')
    engine = db.Column(db.String(100), comment='引擎')
    cron = db.Column(db.String(100), comment='cron定时任务')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')

class Engine(db.Model):
    __tablename__ = 'Engine'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(500), comment='引擎名称')
    engine_name = db.Column(db.String(500), comment='引擎名称')
    engine_num = db.Column(db.String(100), comment='数量')
    note = db.Column(db.TEXT(65535), comment='备注')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class SubTask(db.Model):
    __tablename__ = 'SubTask'
    id = db.Column(db.String(100), primary_key=True)
    task_engine = db.Column(db.String(100), comment='任务引擎')
    task_target = db.Column(db.TEXT(65535), comment='任务目标')
    task_status = db.Column(db.String(10), comment='任务状态')
    is_save = db.Column(db.Boolean(), comment='是否保存')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源类型')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class Domain(db.Model):
    __tablename__ = 'Domain'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), comment='域名')
    domain_type = db.Column(db.String(100), comment='域名解析方式')
    record = db.Column(db.String(100), comment='解析记录')
    ips = db.Column(db.String(100), comment='IPS')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class IP(db.Model):
    __tablename__ = 'IP'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), comment='IP')
    domain = db.Column(db.String(100), comment='域名')
    area = db.Column(db.String(100), comment='地理位置')
    is_cdn = db.Column(db.String(10), comment='是否是CDN')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class Port(db.Model):
    __tablename__ = 'Port'
    id = db.Column(db.Integer, primary_key=True)
    ip_port = db.Column(db.String(100), comment='IP:Port')
    protocol = db.Column(db.String(100), comment='协议')
    service = db.Column(db.String(100), comment='服务')
    product = db.Column(db.String(100), comment='产品')
    version = db.Column(db.String(100), comment='版本')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class Url(db.Model):
    __tablename__ = 'Url'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), comment='url地址')
    status_code = db.Column(db.String(100), comment='状态码')
    title = db.Column(db.String(100), comment='标题')
    content_length = db.Column(db.String(100), comment='内容长度')
    screenshot = db.Column(db.TEXT(65535), comment='截屏')
    cms = db.Column(db.String(100), comment='指纹')
    is_waf = db.Column(db.String(10), comment='是否存在waf')
    raw_response = db.Column(db.String(6535), comment='原始返回信息')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class UrlPath(db.Model):
    __tablename__ = 'UrlPath'
    id = db.Column(db.Integer, primary_key=True)
    url_full = db.Column(db.String(100), comment='url地址')
    status_code = db.Column(db.String(10), comment='状态码')
    title = db.Column(db.String(100), comment='标题')
    content_length = db.Column(db.String(100), comment='内容长度')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class Vuln(db.Model):
    __tablename__ = 'Vuln'
    id = db.Column(db.Integer, primary_key=True)
    vuln_addr = db.Column(db.String(100), comment='地址')
    vuln_name = db.Column(db.String(100), comment='漏洞名称')
    vuln_level = db.Column(db.String(10), comment='漏洞级别')
    vuln_payload = db.Column(db.TEXT(65535), comment='利用代码')
    vuln_raw_response = db.Column(db.TEXT(65535), comment='原始响应')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')



class ICP(db.Model):
    __tablename__ = 'ICP'
    id = db.Column(db.Integer, primary_key=True)
    contentTypeName = db.Column(db.String(100), comment='')
    domain = db.Column(db.String(100), comment='')
    domainId = db.Column(db.String(100), comment='')
    leaderName = db.Column(db.String(100), comment='')
    limitAccess = db.Column(db.String(100), comment='')
    mainId = db.Column(db.String(100), comment='')
    mainLicence = db.Column(db.String(100), comment='')
    natureName = db.Column(db.String(100), comment='')
    serviceId = db.Column(db.String(100), comment='')
    serviceLicence = db.Column(db.String(100), comment='')
    unitName = db.Column(db.String(100), comment='')
    updateRecordTime = db.Column(db.String(100), comment='')
    status = db.Column(db.String(100), comment='状态')
    task_name = db.Column(db.String(100), comment='任务名称')
    source = db.Column(db.String(100), comment='来源')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')


class GithubRepos(db.Model):
    __tablename__ = 'GithubRepos'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), comment='任务名称')
    html_url = db.Column(db.String(500), comment='主页')
    description = db.Column(db.String(500), comment='描述')
    updated_at = db.Column(db.String(500), comment='更新时间')
    create_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime(timezone=True), comment='更新时间')
