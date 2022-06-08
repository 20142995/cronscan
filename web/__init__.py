from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_script import Manager
from flask_restful import Api
from flask_apscheduler import APScheduler

from celery import Celery


app = Flask(__name__)
app.config.from_object(Config)
scheduler = APScheduler()


# 建立数据库关系
db = SQLAlchemy(app)
manager = Manager(app)

migrate = Migrate(app, db)
# 绑定api
api = Api(app)




# 视图
from web.route import home

# api
from web.route.user_api import UserLogin
from web.route.task_api import TaskManage
from web.route.sub_task_api import SubTaskManage
from web.route.ip_api import IPManage
from web.route.domain_api import DomainManage
from web.route.port_api import PortManage
from web.route.url_api import UrlManage
from web.route.url_path_api import UrlPathManage
from web.route.vuln_api import VulnManage
from web.route.icp_api import ICPManage

from web.route.target_api import TargetManage
from web.route.engine_api import EngineManage

from web.route.githubrepos_api import GithubReposManage



api.add_resource(UserLogin, '/api/user/login', endpoint='api_user_login')
api.add_resource(TaskManage, '/api/task/manage', endpoint='api_task_manage')
api.add_resource(SubTaskManage, '/api/sub_task/manage', endpoint='api_sub_task_manage')
api.add_resource(IPManage, '/api/ip/manage', endpoint='api_ip_manage')
api.add_resource(DomainManage, '/api/domain/manage', endpoint='api_domain_manage')
api.add_resource(PortManage, '/api/port/manage', endpoint='api_port_manage')
api.add_resource(UrlManage, '/api/url/manage', endpoint='api_url_manage')
api.add_resource(UrlPathManage, '/api/url_path/manage', endpoint='api_url_path_manage')
api.add_resource(VulnManage, '/api/vuln/manage', endpoint='api_vuln_manage')
api.add_resource(ICPManage, '/api/icp/manage', endpoint='api_icp_manage')

api.add_resource(EngineManage, '/api/engine/manage', endpoint='api_engine_manage')

api.add_resource(TargetManage, '/api/target/manage', endpoint='api_target_manage')
api.add_resource(GithubReposManage, '/api/githubrepos/manage', endpoint='api_githubrepos_manage')









