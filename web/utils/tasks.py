import datetime
from celery import Celery
from celery.result import AsyncResult
from web import db
from web.models import Domain, Target,SubTask,ICP,Engine, Url,UrlPath,IP, Vuln,Port,GithubRepos,Task
from web.config import Config
from sqlalchemy import and_
from web.utils.log import Logger
import threading
from functools import wraps
import os
import re
from web.utils.dingtalk import send_text


def is_ip(value):
    ''' 
    判断是否是IP
    :param value eg: 127.0.0.1
    :return True or False
    '''
    pattern_ip = re.compile(
        r'^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}'
        r'|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d'
        r'|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$'
    )
    return True if pattern_ip.match(value) else False
def is_domain(value):
    ''' 
    判断是否是域名
    :param value eg: baidu.com
    :return True or False
    '''
    pattern_domain = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return True if pattern_domain.match(value) else False


log = Logger()
celery_app = Celery(broker=Config.CELERY_BROKER_URL,
                    backend=Config.CELERY_RESULT_BACKEND)
celery_app.conf.update(CELERY_TASK_SERIALIZER='json', CELERY_RESULT_SERIALIZER='json', CELERY_ACCEPT_CONTENT=[
                       'json'], CELERY_TIMEZONE='Asia/Shanghai', CELERY_ENABLE_UTC=False,)

def new_thread(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # print(f'函数的名字：{func.__name__}')
        # print(f'函数的位置参数：{args}')
        thread = threading.Thread(target=func, args=args,kwargs=kwargs)
        thread.daemon = True
        thread.start()
    return inner
@new_thread
def update_engine():
    '''更新引擎'''
    log.info('update_engine')
    engines = {}
    try:
        celery_active = celery_app.control.inspect().active()
    except:
        return
    if celery_active:
        for k, _ in celery_active.items():
            name = k.split('@')[1].split('_', 1)[0]
            engines.setdefault(name,0)
            engines[name] += 1
    for k,v in engines.items():
        engine = Engine.query.filter(Engine.engine_name==k).first()
        if engine:
            engine.engine_num = v
            engine.update_time = datetime.datetime.now()
            db.session.commit()
        else:
            db.session.execute(Engine.__table__.insert(),[{'engine_name':k,'engine_num':v}])
            db.session.commit()
    
    log.info('update_engine over')

@new_thread
def create_sub_task(task_name, source, engine_name, target):
    '''创建celery子任务'''
    log.info('create_sub_task')
    if engine_name == 'rad':
        task_id = celery_app.send_task(engine_name+'.run', (target,True), queue=engine_name).id
    else:
        task_id = celery_app.send_task(engine_name+'.run', (target,), queue=engine_name).id
    sub1 = SubTask(id=task_id, task_engine=engine_name, task_target=str(target), task_status=AsyncResult(
        task_id, app=celery_app).status, is_save=False, source=source, task_name=task_name)
    db.session.add(sub1)
    db.session.commit()
    log.info('create_sub_task over')


@new_thread
def run_task(task_id):
    '''运行任务'''
    log.info('run_task {}'.format(task_id))
    task = Task.query.filter(Task.id==task_id).first()
    for engine_name in task.engine.split(','):
        engine = Engine.query.filter(Engine.engine_name==engine_name).first()
        if engine_name in ['area','domaininfo','ehole','githubrepos']:
            targets = [_.target for _ in Target.query.filter(Target.target_group==task.task_name).filter(Target.target_type==engine.target_type).all()]
            create_sub_task(task.task_name, engine_name, engine_name, targets)
        else:
            for target in Target.query.filter(Target.target_group==task.task_name).filter(Target.target_type==engine.target_type).all():
                create_sub_task(task.task_name, engine_name, engine_name, target.target)
    log.info('run_task over')

def deal_icpbeian(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('serviceId'):
            icp = ICP.query.filter(ICP.serviceId==item['serviceId']).first()
            if icp:
                icp.status = '遗留'
                db.session.commit()
            else:
                item['status'] = '新增'
                db.session.execute(ICP.__table__.insert(),[item])
                db.session.commit()

def deal_subdomain(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('domain'):
            domain = Domain.query.filter(Domain.domain==item['domain']).first()
            if domain:
                domain.status = '遗留'
                db.session.commit()
            else:
                item['status'] = '新增'
                db.session.execute(Domain.__table__.insert(),[item])
                db.session.commit()

def deal_domaininfo(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('domain'):
            domain = Domain.query.filter(Domain.domain==item['domain']).first()
            if domain:
                domain.status = '遗留'
                domain.domain_type = item['type']
                domain.record = ','.join(item['record'])
                domain.ips = ','.join(item['ips'])
                db.session.commit()
            else:
                item['status'] = '新增'
                item['record'] = ','.join(item['record'])
                item['ips'] = ','.join(item['ips'])
                db.session.execute(Domain.__table__.insert(),[item])
                db.session.commit()

def deal_area(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('ip'):
            ip = IP.query.filter(IP.ip==item['ip']).first()
            if ip:
                ip.status = '遗留'
                ip.area = item['area']
                db.session.commit()
            else:
                item['status'] = '新增'
                db.session.execute(IP.__table__.insert(),[item])
                db.session.commit()

def deal_githubrepos(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name})
        if item.get('html_url'):
            repo = GithubRepos.query.filter(GithubRepos.html_url==item['html_url']).first()
            if repo:
                if repo.updated_at != item['updated_at']:
                    if os.environ.get('DINGTALK_TOKEN',''):
                        send_text('消息:\n主页: {}\n描述: {}\n更新时间: {}'.format(item['html_url'],item['description'],item['updated_at']), token=os.environ['DINGTALK_TOKEN'], secret=os.environ.get('DINGTALK_SECRET', ''))
                    repo.updated_at = item['updated_at']
                    db.session.commit()
            else:
                db.session.execute(GithubRepos.__table__.insert(),[item])
                db.session.commit()

def deal_url(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('url'):
            url = Url.query.filter(Url.url==item['url']).first()
            if url:
                url.status = '遗留'
                db.session.commit()
            else:
                item['status'] = '新增'
                db.session.execute(Url.__table__.insert(),[item])
                db.session.commit()

def deal_urlpath(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('url'):
            url = UrlPath.query.filter(UrlPath.url==item['url']).first()
            if url:
                url.status = '遗留'
                db.session.commit()
            else:
                item['status'] = '新增'
                db.session.execute(UrlPath.__table__.insert(),[item])
                db.session.commit()

def deal_portscan(task_name,tool,items):
    for item in items:
        item.update({'task_name': task_name,'source': tool})
        if item.get('ip_port'):
            port = Port.query.filter(Port.ip_port==item['ip_port']).first()
            if port:
                port.status = '遗留'
                db.session.commit()
            else:
                item['status'] = '新增'
                db.session.execute(Port.__table__.insert(),[item])
                db.session.commit()
@new_thread
def deal_target():
    items = {}
    for domain in Domain.query.filter().all():
        if not Target.query.filter(Target.target==domain.domain).filter(Target.target_type=='subdomain').first():
            item = {'target_group':domain.task_name,'target_type':'subdomain','target':domain.domain,'note':domain.source}
            items[item['target']] = item
        if domain.ips:
            for ip in domain.ips.split(','):
                if not Target.query.filter(Target.target==ip).filter(Target.target_type=='ip').first():
                    item = {'target_group':domain.task_name,'target_type':'ip','target':ip,'note':domain.source}
                    items[item['target']] = item
    for icp in ICP.query.filter().all():
        for i in icp.domain.split(','):
            if is_ip(i):
                if not Target.query.filter(Target.target==ip).filter(Target.target_type=='ip').first():
                    item = {'target_group':domain.task_name,'target_type':'ip','target':i,'note':'icpbeian'}
                    items[item['target']] = item
            if is_domain(i):
                if not Target.query.filter(Target.target==icp.domain).filter(Target.target_type=='domain').first():
                    item = {'target_group':icp.task_name,'target_type':'domain','target':i,'note':'icpbeian'}
                    items[item['target']] = item     
            
    db.session.execute(Target.__table__.insert(),items.items())
    db.session.commit()


@new_thread
def update_sub_task():
    '''更新子任务状态及临时结果保存到子任务'''
    log.info('update_sub_task')
    for task in SubTask.query.filter(SubTask.task_status != 'SUCCESS').all():
        task_status = AsyncResult(task.id, app=celery_app).status
        if task_status == 'SUCCESS':
            if AsyncResult(task.id, app=celery_app).ready():
                task.task_status = task_status
            task.update_time = datetime.datetime.now()
            db.session.commit()
    log.info('update_sub_task over')

@new_thread
def update_sub_task_result():
    log.info('update_sub_task_result')
    for task in SubTask.query.filter(and_(SubTask.task_status == 'SUCCESS' , SubTask.is_save == False)).all():
        try:
            result = AsyncResult(task.id, app=celery_app).result
        except:
            log.info('{}/{} not found'.format(task.id,task.task_name))
            task.is_save = True
            task.update_time = datetime.datetime.now()
            db.session.commit()
            continue
        log.info('update_sub_task_result {}/{}/{}'.format(task.task_name,result['tool'],len(result['result'])))
        if result['tool'] in ['icpbeian']:
            deal_icpbeian(task.task_name,result['tool'],result['result'])
        if result['tool'] in ['subfinder','ksubdomain']:
            deal_subdomain(task.task_name,result['tool'],result['result'])
        if result['tool'] in ['area']:
            deal_area(task.task_name,result['tool'],result['result'])
        if result['tool'] in ['domaininfo']:
            deal_domaininfo(task.task_name,result['tool'],result['result'])         
        if result['tool'] in ['ehole']:
            deal_url(task.task_name,result['tool'],result['result'])    
        if result['tool'] in ['bakfile','jsfinder']:
            deal_urlpath(task.task_name,result['tool'],result['result'])  
        if result['tool'] in ['portscan']:
            deal_portscan(task.task_name,result['tool'],result['result'])
        if result['tool'] in ['githubrepos']:
            deal_githubrepos(task.task_name,result['tool'],result['result'])

        task.is_save = True 
        task.update_time = datetime.datetime.now()
        db.session.commit()
    # deal_target()
    log.info('update_sub_task_result over')

