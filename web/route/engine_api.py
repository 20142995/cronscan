from flask import json, escape
from flask_restful import reqparse, Resource
from web import db
from web.models import Engine
from web.utils.common import login_required, message
from sqlalchemy import or_
from web import scheduler
from web.utils.tasks import run_task


class EngineManage(Resource):
    '''任务日志管理'''

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("engine_id", type=str, location='json')
        self.parser.add_argument("engine_name", type=str, location='json')
        self.parser.add_argument("target_type", type=str, location='json')
        self.parser.add_argument("note", type=str, location='json')
        self.parser.add_argument("page", type=int)
        self.parser.add_argument("limit", type=int)
        self.parser.add_argument("searchParams", type=str)


    @login_required
    def get(self):
        '''查询'''
        args = self.parser.parse_args()
        key_page = args.page if not args.page is None else 1
        key_limit = args.limit if not args.limit is None else 20
        key_searchParams = args.searchParams
        count = Engine.query.count()
        jsondata = {'code': 0, 'msg': '', 'count': count,'data': []}
        if count == 0: return jsondata
        if key_searchParams:
            try:
                search_dict = json.loads(key_searchParams)
            except:
                search_dict = {}
            if 'keyword' in search_dict:
                paginate1 = Engine.query.filter(or_(getattr(Engine,_).like("%" + search_dict['keyword'] + "%") for _ in ['engine_name']))
        else:
            paginate1 = Engine.query.filter()
        jsondata.update({'count': paginate1.count()})
        paginate1 = paginate1.order_by(Engine.create_time.desc())
        paginate = paginate1.limit(key_limit).offset((key_page - 1) * key_limit).all()
        if paginate:
            index = (key_page - 1) * key_limit + 1
            data = []
            for i in paginate:
                data1 = {}
                data1['id'] = index
                data1['engine_id'] = i.id
                data1['engine_name'] = i.engine_name
                data1['target_type'] = i.target_type
                data1['engine_num'] = i.engine_num
                data1['note'] = i.note
                data1['create_time'] = i.create_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if i.create_time else ''
                data1['update_time'] = i.update_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if i.update_time else ''
                index += 1
                data.append(data1)
            jsondata.update({'data': data})
        return jsondata
    @login_required
    def post(self):
        '''增加'''
        args = self.parser.parse_args()
        key_engine = args.engine_name
        key_type = args.target_type
        key_note = args.note
        if not key_engine or not key_type:
            return message(500, '')
        engine1 = Engine(engine_name=key_engine,target_type=key_type, note=key_note)
        db.session.add(engine1)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')
        return message(200, '')

    @login_required
    def delete(self):
        '''删除'''
        args = self.parser.parse_args()
        key_id = args.engine_id
        _query = Engine.query.filter(Engine.id == key_id).first()
        if not _query:
            return message(202, '')
        db.session.delete(_query)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')

        return message(200, '')