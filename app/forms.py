from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import IntegerField
from wtforms.validators import DataRequired


class ImageForm(FlaskForm):
    img = FileField('image', validators=[FileRequired()])
    w = IntegerField('width', validators=[DataRequired()])
    h = IntegerField('height', validators=[DataRequired()])
