from web import app,scheduler
from web import db
from web.models import User
from werkzeug.security import generate_password_hash
from web.utils.tasks import update_engine,update_sub_task,update_sub_task_result  

@app.before_first_request
def init():
    u = User.query.filter_by().first()
    if u is None:
        u = User(username='admin',
                 password=generate_password_hash("admin@123"))
        db.session.add(u)
        db.session.commit()
    job1 = scheduler.get_job('update_sub_task')
    if not job1:scheduler.add_job(func=update_sub_task,id='update_sub_task',trigger='cron',second="0", minute="*/2",replace_existing=True,timezone='Asia/Shanghai')
    job2 = scheduler.get_job('update_sub_task_result')
    if not job2:scheduler.add_job(func=update_sub_task_result,id='update_sub_task_result',trigger='cron',second="0", minute="*/2",replace_existing=True,timezone='Asia/Shanghai')
    job3 = scheduler.get_job('update_engine')
    if not job3:scheduler.add_job(func=update_engine,id='update_engine',trigger='cron',second="0", minute="*/10",replace_existing=True,timezone='Asia/Shanghai')
 
if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0')