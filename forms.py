from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
	"""Form for adding users."""

	username = StringField('username', validators=[DataRequired()])
	email = StringField('email', validators=[DataRequired(), Email()])
	password = PasswordField('password', validators=[Length(min=7)])

class LoginForm(FlaskForm):
	"""Login form."""

	username = StringField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[Length(min=7)])

class UserEditForm(FlaskForm):
	"""Form to edit user."""

	username = StringField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[Length(min=7)])

class SearchForm(FlaskForm):
	artist = StringField('artist', validators=[DataRequired()])
	song = StringField('song', validators=[DataRequired()])
	submit = SubmitField('search', render_kw={'class': 'btn btn-success btn btn-block'}) 