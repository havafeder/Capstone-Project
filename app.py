import json, requests
from socket import INADDR_UNSPEC_GROUP
import os
from flask import Flask, request, render_template, redirect, session, g, flash, url_for, abort
from forms import UserAddForm, LoginForm, SearchForm
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Song, Likes
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import pdb 


CURR_USER_KEY = "curr_user"

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///genius'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "hehe secret")
toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# genius = lyricsgenius.Genius('2c8DFT-d-NxgF0yAM14oQYu44LlpWvM1TZ9sLpl_kAH24DUQVSAbcVn_ZKJMw2lJ',
# skip_non_songs = True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

# url = 'https://api.lyrics.ovh/v1/maroon5/sugar'
# response = requests.get(url)
# data = json.loads(response.text)
# db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# logging in and logging out functions:

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# homepage: 

@app.route('/')
def home():

    if g.user:

        liked_song_ids = [sng.id for sng in g.user.likes]

        return render_template('home.html', songs=liked_song_ids)

    else:
        return render_template('home_anon.html')

# searching:


@app.route('/search', methods=['POST', 'GET'])
def search_lyrics():
    """Handle search of lyrics"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
        
    form = SearchForm()

    if form.validate_on_submit():
        artist = form.artist.data
        song_name = form.song.data
        url = f'https://api.lyrics.ovh/v1/{artist}/{song_name}'
        response = requests.get(url)
        data = json.loads(response.text)
        lyrics = data['lyrics']
        user_id = g.user.id
        song = Song(
            user_id=user_id,
            title=song_name,
            artist=artist,
            lyrics=lyrics
        )
        db.session.add(song)
        db.session.commit()
        return render_template("results.html", data=data, url=url, 
        artist=artist, lyrics=lyrics, song=song, song_name=song_name)
    
    else:
        return render_template("search.html", form=form)

# saving lyrics to profile:

@app.route('/search/save/<int:song_id>', methods=['POST', 'GET'])
def save_lyrics(song_id):
    """Save lyrics to user profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    liked_song = Song.query.filter_by(id = song_id).first()
    id_song = liked_song.id
    title = liked_song.title
    artist=liked_song.artist
    lyrics=liked_song.lyrics
    id_user = g.user.id
    like = Likes(
        user_id=id_user,
        song_id_=id_song,
        title=title,
        artist=artist,
        lyrics=lyrics
    )
    db.session.add(like)
    db.session.commit()
    return render_template("home.html", id_user=id_user, like=like, title=title, artist=artist,
    lyrics=lyrics, liked_song=liked_song, id_song=id_song)

# displaying likes:

@app.route('/likes', methods=['POST', 'GET'])
def display_likes():
    """Show user's saved songs."""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    songs = g.user.likes
    
    return render_template("likes.html", songs=songs)

# displaying lyrics of liked song:

@app.route('/likes/<int:song_id>', methods=['GET'])
def show_lyrics(song_id):
    """Show lyrics of saved song"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    song = Likes.query.filter_by(id = song_id).first()

    return render_template("show_song.html", song=song)


# signing up:

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle User sign up"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username is taken", "danger")
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect('/')

    else:

        return render_template('signup.html', form=form)

# logging in, logging out:

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data,
                                password=form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect('/')
        
        flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    """handle logout of user."""
    do_logout()
    flash("You have logged out", "success")
    return redirect('/login')

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
