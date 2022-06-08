from flask import json, escape
from flask_restful import reqparse, Resource
from web import db
from web.models import Domain
from web.utils.common import login_required, message
from sqlalchemy import or_

class DomainManage(Resource):
    '''域名管理'''

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("page", type=int)
        self.parser.add_argument("limit", type=int)
        self.parser.add_argument("searchParams", type=str)
        self.parser.add_argument("domain", type=str)

    @login_required
    def get(self):
        '''查询'''
        args = self.parser.parse_args()
        key_page = args.page if not args.page is None else 1
        key_limit = args.limit if not args.limit is None else 20
        key_searchParams = args.searchParams
        count = Domain.query.count()
        jsondata = {'code': 0, 'msg': '', 'count': count,'data': []}
        if count == 0: return jsondata
        if key_searchParams:
            try:
                search_dict = json.loads(key_searchParams)
            except:
                search_dict = {}
            if 'keyword' in search_dict:
                paginate1 = Domain.query.filter(or_(getattr(Domain,_).like("%" + search_dict['keyword'] + "%") for _ in ['task_name']))
        else:
            paginate1 = Domain.query.filter()
        jsondata.update({'count': paginate1.count()})
        paginate1 = paginate1.order_by(Domain.create_time.desc()).order_by(Domain.update_time.desc())
        paginate = paginate1.limit(key_limit).offset((key_page - 1) * key_limit).all()
        if paginate:
            index = (key_page - 1) * key_limit + 1
            data = []
            for i in paginate:
                data1 = {}
                data1['id'] = index
                data1['domain'] = i.domain
                data1['domain_type'] = i.domain_type
                data1['record'] = i.record
                data1['domain'] = i.domain
                data1['ips'] = i.ips
                data1['task_name'] = i.task_name
                data1['source'] = i.source
                data1['create_time'] = i.create_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if i.create_time else ''
                data1['update_time'] = i.update_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if i.update_time else ''
                index += 1
                data.append(data1)
            jsondata.update({'data': data})
        return jsondata

    @login_required
    def delete(self):
        '''删除'''
        args = self.parser.parse_args()
        key_domain = escape(args.domain)
        _query = Domain.query.filter(Domain.domain == key_domain).first()
        if not _query:
            return message(202, '')
        db.session.delete(_query)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')
        return message(200, '')
