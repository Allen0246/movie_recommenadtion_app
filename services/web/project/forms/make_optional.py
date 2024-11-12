from wtforms.validators import DataRequired, InputRequired, Optional

def make_optional(field):
    field.validators=[Optional()]
