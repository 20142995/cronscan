from flask import json, escape
from flask_restful import reqparse, Resource
from web import db
from web.models import Target, Task
from web.utils.common import login_required, message
from sqlalchemy import or_
from web import scheduler
from web.utils.tasks import run_task

class TaskManage(Resource):
    '''任务管理'''

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("task_id", type=str, location='json')
        self.parser.add_argument("task_name", type=str, location='json')
        self.parser.add_argument("engine", type=str, location='json')
        self.parser.add_argument("cron", type=str, location='json')
        self.parser.add_argument("page", type=int)
        self.parser.add_argument("limit", type=int)
        self.parser.add_argument("searchParams", type=str)
        self.parser.add_argument("action", type=str)

    @login_required
    def get(self):
        '''查询'''
        args = self.parser.parse_args()
        key_page = args.page if not args.page is None else 1
        key_limit = args.limit if not args.limit is None else 20
        key_searchParams = args.searchParams
        count = Task.query.count()
        jsondata = {'code': 0, 'msg': '', 'count': count,'data': []}
        if count == 0: return jsondata
        if key_searchParams:
            try:
                search_dict = json.loads(key_searchParams)
            except:
                search_dict = {}
            if 'keyword' in search_dict:
                paginate1 = Task.query.filter(or_(getattr(Task,_).like("%" + search_dict['keyword'] + "%") for _ in ['task_name']))
        else:
            paginate1 = Task.query.filter()
        jsondata.update({'count': paginate1.count()})
        paginate1 = paginate1.order_by(Task.create_time.desc()).order_by(Task.update_time.desc())
        paginate = paginate1.limit(key_limit).offset((key_page - 1) * key_limit).all()
        if paginate:
            index = (key_page - 1) * key_limit + 1
            data = []
            for i in paginate:
                data1 = {}
                data1['id'] = index
                data1['task_id'] = i.id
                data1['task_name'] = i.task_name
                data1['engine'] = i.engine
                data1['cron'] = i.cron
                
                ret = scheduler.get_job('{}-{}'.format(i.task_name,i.id))
                if ret:
                    status = 'Runing...' if ret.next_run_time != None else 'Pause...'
                    update_time = ret.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if ret.next_run_time != None else ''
                else:
                    update_time = ''
                    status = 'Stop...'
                data1['status'] = status if i.cron else ''
                data1['create_time'] = i.create_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if i.create_time else ''
                data1['update_time'] = update_time
                index += 1
                data.append(data1)
            jsondata.update({'data': data})
        return jsondata

    @login_required
    def post(self):
        '''增加'''
        args = self.parser.parse_args()
        key_name = args.task_name
        key_engine = args.engine
        key_cron = args.cron
        if not key_name or not key_engine:
            return message(500, '')
        _query = Task.query.filter(Task.task_name == key_name).filter(Task.engine == key_engine).filter(Task.cron == key_cron).first()
        if _query:
            return message(201, '')
        task1 = Task(task_name=key_name,engine=key_engine, cron=key_cron)
        db.session.add(task1)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')
        _query = Task.query.filter(Task.task_name == key_name).filter(Task.engine == key_engine).filter(Task.cron == key_cron).first()
        if key_cron:
            cron = key_cron.split(' ')
            cron_rel = dict(second=cron[0], minute=cron[1], hour=cron[2], day=cron[3], month=cron[4], day_of_week=cron[5])
            scheduler.add_job(func=run_task,id="{}-{}".format(key_name,_query.id), args=[_query.id],trigger='cron',**cron_rel,replace_existing=True,timezone='Asia/Shanghai')
        else:
            run_task(_query.id)
        return message(200, '')

    @login_required
    def delete(self):
        '''删除'''
        args = self.parser.parse_args()
        key_id = args.task_id
        key_name = args.task_name
        _query = Task.query.filter(Task.id == key_id).first()
        if not _query:
            return message(202, '')
        db.session.delete(_query)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')
        try:
            scheduler.remove_job("{}-{}".format(key_name,key_id))
        except:
            pass
        return message(200, '')

    @login_required
    def put(self):
        '''修改'''
        args = self.parser.parse_args()
        key_id = args.task_id
        key_name = args.task_name
        key_cron = args.cron
        key_action = args.action
        if key_action == 'pause':
            try:
                scheduler.pause_job('{}-{}'.format(key_name,key_id))
            except:
                pass
        elif key_action == 'resume':
            try:
                scheduler.resume_job('{}-{}'.format(key_name,key_id))
            except:
                pass
        elif key_action == 'start':
            if key_cron:
                cron = key_cron.split(' ')
                cron_rel = dict(second=cron[0], minute=cron[1], hour=cron[2], day=cron[3], month=cron[4], day_of_week=cron[5])
                scheduler.add_job(func=run_task,id='{}-{}'.format(key_name,key_id), args=[key_id],trigger='cron',**cron_rel,replace_existing=True,timezone='Asia/Shanghai')
        return message(200, '')

