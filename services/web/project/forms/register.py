from flask_wtf import FlaskForm
from wtforms import PasswordField, IntegerField, StringField
from wtforms.validators import InputRequired ,EqualTo, Length, Regexp, ValidationError
from wtforms.widgets.core import HiddenInput
from ..models.auth import User, Role


class RegisterForm(FlaskForm):
    user_id = IntegerField(widget=HiddenInput())
    username = StringField('Username', [InputRequired(message='This field is required.')])
    password = PasswordField('Password', [InputRequired(message='This field is required.'),
                                        EqualTo('confirm_password', message='Password verification failed.'),
                                        Length(min=8, message='Minimum 8 characters.'),
                                        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$',
                                        message='Must contain at least one uppercase letter, one lowercase letter, one number, and one other character: @$!%*?&')
                                        ],
                                        description='The password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one other character: @$!%*?&')
    confirm_password = PasswordField('Password again', [InputRequired(message='This field is required.')])

    def validate_username(form, field):
        user_id = form.user_id.data
        if user_id:
            user = User.query.filter(User.username == field.data).filter(User.id!=user_id).first()
        else:
            user = User.query.filter(User.username == field.data).first()
        if user:
            raise ValidationError('The Username is already taken.')