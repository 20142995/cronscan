from flask import session, url_for, render_template, jsonify

from web import app
from web.utils.common import login_required

from io import BytesIO
from flask import session, make_response, redirect, url_for, render_template
from web import app
from web.models import Engine, Target
from web.utils.captcha.captcha import get_verify_code
from web.utils.common import login_required


@app.route('/html/home/index')
@login_required
def html_home_index():
    '''框架首页'''
    return render_template('index.html', username=session['username'])


@app.route('/home/init')
@login_required
def api_menu_init():
    '''菜单栏目'''
    caching_menu = {'clearUrl': url_for('api_caching_clear')}  # 缓存菜单
    home_menu = {'title': '主页', 'icon': 'fa fa-home', 'href': ''}  # 主页菜单
    logo_menu = {'title': '', 'image': url_for(
        'static', filename='images/logo.png'), 'href': ''}  # logo菜单
    assets_menu = {'title': '定时扫描', 'icon': 'fa fa-address-book', 'child': [
        {'title': '任务', 'href': '', 'icon': 'fa fa-tachometer',
            'child': [
                {'title': '目标', 'href': url_for('html_target_manage'), 'icon': 'fa fa-globe', 'target': '_self'},
                {'title': '任务', 'href': url_for('html_task_manage'), 'icon': 'fa fa-globe', 'target': '_self'},
                {'title': '子任务', 'href': url_for('html_sub_task_manage'), 'icon': 'fa fa-globe', 'target': '_self'},
                {'title': '引擎', 'href': url_for('html_engine_manage'), 'icon': 'fa fa-globe', 'target': '_self'}
                ]},
        {'title': '结果', 'href': '', 'icon': 'fa fa-globe',
            'child': [
                {'title': 'IP', 'href': url_for('html_ip_manage'), 'icon': 'fa fa-cube', 'target': '_self'},
                {'title': '域名', 'href': url_for('html_domain_manage'), 'icon': 'fa fa-cube', 'target': '_self'},
                {'title': '端口服务', 'href': url_for('html_port_manage'), 'icon': 'fa fa-cube', 'target': '_self'},
                {'title': 'URL', 'href': url_for('html_url_manage'),'icon': 'fa fa-paw', 'target': '_self'},
                {'title': 'ICP', 'href': url_for('html_icp_manage'),'icon': 'fa fa-paw', 'target': '_self'},
                {'title': 'github repos', 'href': url_for('html_githubrepos_manage'),'icon': 'fa fa-paw', 'target': '_self'},
        #         ]},
        # {'title': '漏洞', 'href': '', 'icon': 'fa fa-cube',
        #     'child': [
                {'title': 'URL路径', 'href': url_for('html_url_path_manage'),'icon': 'fa fa-paw', 'target': '_self'},
                {'title': '漏洞', 'href': url_for('html_vuln_manage'), 'icon': 'fa fa-user-secret', 'target': '_self'}, ]},
    ]}
    system_menu = {}
    menu_dict = {
        'clearInfo': caching_menu,
        'homeInfo': home_menu,
        'logoInfo': logo_menu,
        'menuInfo': {
            'a-assets': assets_menu,
            # 'c-system': system_menu
        }
    }  # 菜单按照字母排序
    return jsonify(menu_dict)

@app.route('/html/domain/manage')
@login_required
def html_domain_manage():
    '''域名资产'''
    return render_template('domain.html')

@app.route('/html/ip/manage')
@login_required
def html_ip_manage():
    '''IP资产'''
    return render_template('ip.html')

@app.route('/html/port/manage')
@login_required
def html_port_manage():
    '''端口资产'''
    return render_template('port.html')

@app.route('/html/sub_task/manage')
@login_required
def html_sub_task_manage():
    '''子任务页面'''
    return render_template('sub_task.html')

@app.route('/html/task/manage')
@login_required
def html_task_manage():
    '''任务管理页面'''
    return render_template('task.html')

@app.route('/html/githubrepos/manage')
@login_required
def html_githubrepos_manage():
    '''页面'''
    return render_template('githubrepos.html')
    
@app.route('/html/engine/manage')
@login_required
def html_engine_manage():
    '''引擎页面'''
    return render_template('engine.html')

@app.route('/html/task/add')
@login_required
def html_task_add():
    '''添加任务页面'''
    target_groups = [_[0] for _ in Target.query.with_entities(Target.target_group).distinct().all()]
    engines = [_[0] for _ in Engine.query.with_entities(Engine.engine_name).distinct().all()]
    return render_template('task_add.html', target_groups=target_groups,engines=engines)

@app.route('/html/target/add')
@login_required
def html_target_add():
    '''添加目标页面'''
    
    return render_template('target_add.html',)
@app.route('/html/engine/add')
@login_required
def html_engine_add():
    '''添加引擎页面'''
    return render_template('engine_add.html',)


@app.route('/html/url/manage')
@login_required
def html_url_manage():
    '''url资产'''
    return render_template('url.html')

@app.route('/html/icp/manage')
@login_required
def html_icp_manage():
    '''icp资产'''
    return render_template('icp.html')

@app.route('/html/url_path/manage')
@login_required
def html_url_path_manage():
    '''url资产'''
    return render_template('url_path.html')

@app.route('/api/user/captcha')
def api_get_code():
    '''图片验证码接口'''
    image, code = get_verify_code()
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/jpeg'
    session['code'] = code
    return response


@app.route('/')
def html_user_login():
    '''user login页面'''
    if 'status' in session:
        return redirect(url_for('html_home_index'), 302)
    return render_template('login.html')


@app.route('/api/user/logout')
@login_required
def api_user_logout():
    '''用户注销'''
    session.pop('status')
    session.pop('username')
    session.pop('login_ip')
    return redirect(url_for('html_user_login'), 302)

@app.route('/html/vuln/manage')
@login_required
def html_vuln_manage():
    '''vuln'''
    return render_template('vuln.html')

@app.route('/html/target/manage')
@login_required
def html_target_manage():
    '''target'''
    return render_template('target.html')

@app.route('/home/clear')
@login_required
def api_caching_clear():
    return jsonify({'code': 1, 'msg': '服务端缓存清理成功'})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
