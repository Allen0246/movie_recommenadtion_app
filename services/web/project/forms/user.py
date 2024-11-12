from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import Form, StringField, PasswordField, HiddenField, StringField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, Regexp, Optional, ValidationError
from ..models.auth import User, Role
from ..models import *
from wtforms.widgets.core import HiddenInput

class ProfilePassForm(FlaskForm):
    password_old = PasswordField('Current password', [InputRequired(message='This field is required.')])
    password_new = PasswordField('New password',   [InputRequired(),EqualTo('password_new2', message='Password verification failed.'),
                                                Length(min=8, message='Minimum 8 characters.'),
                                                Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$',
                                                message='Must contain at least one uppercase letter, one lowercase letter, one number, and one other character: @$!%*?&')],
                                                description='The password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one other character: @$!%*?&')
    password_new2 = PasswordField('New password again', [InputRequired(message='This field is required.')])

    def validate_password_old(form, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Incorrect password')


class UserForm(FlaskForm):
    user_id = IntegerField(widget=HiddenInput())
    username = StringField('Username', [InputRequired(message='This field is required.')])
    password = PasswordField('Password', [InputRequired(message='This field is required.'),
                                        EqualTo('confirm', message='Password verification failed.'),
                                        Length(min=8, message='Minimum 8 characters.'),
                                        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$',
                                        message='Must contain at least one uppercase letter, one lowercase letter, one number, and one other character: @$!%*?&')
                                        ],
                                        description='The password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one other character: @$!%*?&')
    confirm = PasswordField('Password again', [InputRequired(message='This field is required.')])
    roles = []
    for role in Role.query.all():
        roles.append((role.name, role.name.capitalize()))
    role = SelectField('Roles', choices=roles)

    def validate_username(form, field):
        user_id = form.user_id.data
        if user_id:
            user = User.query.filter(User.username == field.data).filter(User.id!=user_id).first()
        else:
            user = User.query.filter(User.username == field.data).first()
        if user:
            raise ValidationError('The Username is already taken.')
