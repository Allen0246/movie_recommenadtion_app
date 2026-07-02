from flask import Blueprint, render_template, jsonify, send_file, request
from flask_login import LoginManager, login_required, current_user
from ..views.auth import role_required, roles_required
import os
import datetime as dt

log_files = Blueprint('log_files', __name__)

@log_files.route('/log_files')
@role_required('admin')
def index():
    json_for_datatable = []
    file_names = os.listdir('/app/project/log')
    for file_name in file_names:
        create_date = dt.datetime.fromtimestamp(os.path.getctime('/app/project/log/{0}'.format(file_name))).strftime("%Y-%m-%d, %H:%M")
        last_modified = dt.datetime.fromtimestamp(os.path.getmtime('/app/project/log/{0}'.format(file_name))).strftime("%Y-%m-%d, %H:%M")
        json_for_datatable.append({'name': file_name, 'create_date': create_date, 'last_modified': last_modified})
    return render_template('logs/index.html', data = json_for_datatable)


@log_files.route('/log_files/view/<file_name>')
@role_required('admin')
def view(file_name):
    path = '/app/project/log/{0}'.format(file_name)
    with open(path, 'r') as file:
        file_data = file.read()
    return render_template('logs/view.html', file_name = file_name, file_data = file_data)


@log_files.route('/log_files/<id>')
@role_required('admin')
def download(id):
    path = '/app/project/log/{0}'.format(id)
    return send_file(path, as_attachment=True)