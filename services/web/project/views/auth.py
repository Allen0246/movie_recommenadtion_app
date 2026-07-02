from flask import Blueprint, redirect, render_template, url_for, request, flash, g
from ..models.auth import User
from ..forms.register import  RegisterForm
from ..forms.login import LoginForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user ,logout_user, login_required, current_user
from .. import db, log, login_manager, app
from functools import wraps

auth = Blueprint('auth', __name__)

def role_required(role: str):
    def _role_required(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if not current_user.has_role(role):
                flash('You do not have access.', 'danger')
                return redirect(url_for('error'))
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log.error(e)
                flash('Error.','danger')
                return redirect(url_for('error'))
        return decorated_view
    return _role_required


def roles_required(roles: list, require_all=False):
    def _roles_required(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if len(roles) == 0:
                raise ValueError('Empty list used when requiring a role.')
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if (require_all and
                not all(current_user.has_role(role) for role in roles)):
                    flash('You do not have access.', 'danger')
                    return redirect(url_for('error'))
            elif (not require_all and
                  not any(current_user.has_role(role) for role in roles)):
                    flash('You do not have access.', 'danger')
                    return redirect(url_for('error'))
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log.error(e)
                flash('Error.','danger')
                return redirect(url_for('error'))
        return decorated_view
    return _roles_required

@auth.route('/register' , methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username and password and confirm_password:
            if password == confirm_password:
                try:
                    new_user = User(username)
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.commit()
                    new_user.set_role(app.config['DEFAULT_USER_ROLE'])
                except Exception as e:
                    flash('Something wrong happen ! Please try again!' , 'danger')
                    return redirect(url_for('auth.register'))
            else:
                flash('Two passwords do not match ! Please try again! ' , 'danger')
                return redirect(url_for('auth.register'))
        flash('Your account has been sucesfully created !', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form = form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# @login_manager.request_loader
# def request_loader(_request):
#   print('using request loader')
#   return load_user_token(_request)


@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']

        roles=[]

        user = (User.query
                .filter_by(username=username)
                .first())
        if user and not user.check_password(password):
            flash('Incorrect username or password. '
                    'Please try again.', 'danger')
            return redirect(url_for('auth.login'))

        try:
            login_user(user)
            log.info('Successfully logged in: {}'.format(username))
        except Exception as e:
            flash('Incorrect username or password.'
                  'Please try again.', 'danger')

            return redirect(url_for('auth.login'))
        flash('You are successfully logged in!', 'success')
        return redirect(url_for('home'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required 
def logout():
    logout_user()
    flash ('Succesfully logged out !', 'success')
    return redirect (url_for('index'))

