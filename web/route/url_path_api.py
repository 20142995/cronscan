from flask import json, escape
from flask_restful import reqparse, Resource
from web import db
from web.models import UrlPath
from web.utils.common import login_required, message
from sqlalchemy import or_


class UrlPathManage(Resource):
    '''URL目录管理'''

    def __init__(self):
        self.parser = reqparse.RequestParser()
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
        count = UrlPath.query.count()
        jsondata = {'code': 0, 'msg': '', 'count': count,'data': []}
        if count == 0: return jsondata
        if key_searchParams:
            try:
                search_dict = json.loads(key_searchParams)
            except:
                search_dict = {}
            if 'keyword' in search_dict:
                paginate1 = UrlPath.query.filter(or_(getattr(UrlPath,_).like("%" + search_dict['keyword'] + "%") for _ in ['task_name']))
        else:
            paginate1 = UrlPath.query.filter()
        jsondata.update({'count': paginate1.count()})
        paginate1 = paginate1.order_by(UrlPath.create_time.desc())
        paginate = paginate1.limit(key_limit).offset((key_page - 1) * key_limit).all()
        if paginate:
            index = (key_page - 1) * key_limit + 1
            data = []
            for i in paginate:
                data1 = {}
                data1['id'] = index
                data1['url_full'] = i.url_full
                data1['status_code'] = i.status_code
                data1['title'] = i.title
                data1['content_length'] = i.content_length
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
        key_url_full = escape(args.url_full)
        _query = UrlPath.query.filter(UrlPath.url_full == key_url_full).first()
        if not _query:
            return message(202, '')
        db.session.delete(_query)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return message(500, '')
        return message(200, '')
