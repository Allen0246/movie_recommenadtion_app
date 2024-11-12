from flask_wtf import FlaskForm
from wtforms import PasswordField, IntegerField, StringField
from wtforms.validators import InputRequired 
from wtforms.widgets.core import HiddenInput


class LoginForm(FlaskForm):
    user_id = IntegerField(widget=HiddenInput())
    username = StringField('USERNAME', [InputRequired(message='This field is required.')])
    password = PasswordField('PASSWORD', [InputRequired(message='This field is required.')])
