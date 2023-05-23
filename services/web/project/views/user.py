from flask import request, render_template
from flask import flash, redirect, url_for, Blueprint, g
from flask_login import LoginManager, login_required, current_user
from .. import login_manager, db, log
from ..models.auth import User, Role, RoleAssignment
from ..views.auth import role_required, roles_required
from ..forms.user import  UserForm, ProfilePassForm
from ..forms.make_optional import make_optional
from datetime import datetime

user = Blueprint('user', __name__)


@user.route('/user')
@role_required('admin')
def index():
    users = (db.session
             .query(User)
             .join(RoleAssignment)
             .with_entities(User.id, User.username, RoleAssignment.role_name)
             .all())
    return render_template('user/index.html', users=users)


@user.route('/user/add', methods=['GET', 'POST'])
@role_required('admin')
def add():
    form = UserForm(request.form)

    rolesForm = []
    for r in Role.query.all():
        rolesForm.append((r.name, r.name.capitalize()))
    form.role.choices = rolesForm

    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']
        user = User(username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        role = request.form.get('role')
        RoleAssignment.create(role, user.get_id())

        log.info("[{0}] The User was created: {1}({2})".format(current_user.username,username,role))
        flash('The new User was successfully created: {0}'.format(username), 'success')
        return redirect(url_for('user.index'))
    return render_template('user/add.html', form=form, user=None)


@user.route('/user/edit/<id>', methods=['GET', 'POST'])
@role_required('admin')
def edit(id):
    user = User.query.filter(User.id == id).first()
    if not user:
        flash('The User does not exist or cannot be edited.', 'info')
        return redirect(url_for('user.index'))
    roles = user.get_roles()
    form = UserForm(obj=user)
    rolesForm = []
    for r in Role.query.all():
        rolesForm.append((r.name, r.name.capitalize()))
    form.role.choices = rolesForm

    password = request.form.get('password')
    if not password or password.strip()=='':
        make_optional(form.password)
        make_optional(form.confirm)
    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        user.set_username(username)
        if password.strip() != '':
            user.set_password(password)
        role = request.form.get('role')
        user.set_role(role)
        db.session.add(user)
        db.session.commit()

        log.info("[{0}] The User has been modified: {1}".format(current_user.username,username))
        flash('The User was successfully modified: {0}'.format(username),'success')
        return redirect(url_for('user.index'))
    else:
        return render_template('user/edit.html',
                               form=form, user=user, roles=roles)


@user.route('/user/delete/<id>', methods=['GET', 'POST'])
@role_required('admin')
def delete(id):
    user = User.query.filter(User.id == id).first()
    if not user:
        flash('The User does not exist or cannot be edited.', 'info')
        return redirect(url_for('user.index'))
    user.remove()
    db.session.commit()

    log.info("[{0}] The User has been deleted: {1}".format(current_user.username,user.username))
    flash('The User has been successfully deleted: {0}'.format(user.username), 'success')
    return redirect(url_for('user.index'))
