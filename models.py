"""SQLAlchemy models for Song Lyrics"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import pdb 
import collections

bcrypt = Bcrypt()
db = SQLAlchemy()


class Song(db.Model):
	"""Mapping song likes to users"""

	__tablename__ = 'songs'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
	title = db.Column(db.Text, nullable=False)
	artist = db.Column(db.Text, nullable=False)
	lyrics = db.Column(db.Text, nullable=False)


class Likes(db.Model):
    """Mapping song likes to users.""" 

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    song_id_ = db.Column(db.Integer, db.ForeignKey('songs.id', ondelete='cascade'))
    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    lyrics = db.Column(db.Text, nullable=False)

class User(db.Model):
	"""User in the system."""

	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)

	email = db.Column(db.Text, nullable=False, unique=True)

	username = db.Column(db.Text, nullable=False, unique=True)

	password = db.Column(db.Text, nullable=False)

	likes = db.relationship('Likes')
	songs = db.relationship('Song')
	
	@classmethod
	def signup(cls, username, email, password):
		"""Sign up user."""

		hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

		user = User(username=username, email=email, password=hashed_pwd)

		db.session.add(user)
		db.session.commit()
		return user

	@classmethod
	def authenticate(cls, username, password):
		"""Authenticate user, find user with the username and password"""

		user = cls.query.filter_by(username=username).first()

		if user:
			is_auth = bcrypt.check_password_hash(user.password, password)
			if is_auth:
				return user

		return False

	def __repr__(self):
		return f"{self.username} - {self.email}"

def connect_db(app):
	"""Connect database to Flask app"""

	db.app = app
	db.init_app(app)