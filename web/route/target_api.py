from flask import json, escape
from flask_restful import reqparse, Resource
from web import db
from web.models import Target
from web.utils.common import login_required, message
from sqlalchemy import or_



class TargetManage(Resource):
    '''目标管理'''

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("target_id", type=str, location='json')
        self.parser.add_argument("target_group", type=str, location='json')
        self.parser.add_argument("target_type", type=str, location='json')
        self.parser.add_argument("target", type=str, location='json')
        self.parser.add_argument("note", type=str, location='json')
        self.parser.add_argument("action", type=str, location='json')
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
        count = Target.query.count()
        jsondata = {'code': 0, 'msg': '', 'count': count, 'data': []}
        if count == 0:
            return jsondata
        if key_searchParams:
            try:
                search_dict = json.loads(key_searchParams)
            except:
                search_dict = {}
            if 'keyword' in search_dict:
                paginate1 = Target.query.filter(or_(getattr(Target, _).like(
                    "%" + search_dict['keyword'] + "%") for _ in ['target_group','target_type','target']))
        else:
            paginate1 = Target.query.filter()
        jsondata.update({'count': paginate1.count()})
        paginate1 = paginate1.order_by(Target.create_time.desc())
        paginate = paginate1.limit(key_limit).offset(
            (key_page - 1) * key_limit).all()
        if paginate:
            index = (key_page - 1) * key_limit + 1
            data = []
            for i in paginate:
                data1 = {}
                data1['id'] = index
                data1['target_id'] = i.id
                data1['target_group'] = i.target_group
                data1['target_type'] = i.target_type
                data1['target'] = i.target
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
        '''增加or删除'''
        args = self.parser.parse_args()
        key_group = args.target_group
        key_type = args.target_type
        key_target = args.target
        key_note = args.note
        key_action = args.action
        if not key_group or not key_type:
            return message(500, '')
        if key_action == 'add' and  key_target:
            db.session.execute(
                Target.__table__.insert(),
                [{"target_group": key_group, "target_type": key_type, "target": i.strip(
                ), "note": key_note} for i in key_target.split('\n') if i.strip()]
            )
        elif key_action == 'del':
            db.session.query(Target).filter(Target.target_group==key_group).filter(Target.target_type==key_type).delete()
        else:
            return message(500, '')
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
        key_id = args.target_id
        _query = Target.query.filter(Target.id == key_id).first()
        if not _query:
            return message(202, '')
        db.session.delete(_query)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')

        return message(200, '')
