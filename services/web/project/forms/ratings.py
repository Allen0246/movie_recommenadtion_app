from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.validators import DataRequired, ValidationError
import datetime

class DateForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired(message='The date is required.')])

    def validate_date(form, field):
        if field.data > datetime.date.today():
            raise ValidationError("The date cannot be in the future!")