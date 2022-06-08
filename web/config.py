
import os
import uuid

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

class Config(object):
    SECRET_KEY = str(uuid.uuid1())
    SQLALCHEMY_DATABASE_URI = os.environ['MYSQL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    CELERY_BROKER_URL = os.environ['BROKER']
    CELERY_RESULT_BACKEND = os.environ['BACKEND']
    # SCHEDULER_API_ENABLED = True
    # SCHEDULER_JOBSTORES = {
    #         'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    #     }
    # SCHEDULER_EXECUTORS = {'default': {'type': 'threadpool', 'max_workers': 10}}


