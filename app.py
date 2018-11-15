from functools import wraps
import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from gwa_spotify_api import SpotifyAuthAPI

SCOPES = [
    'user-read-email',
    'user-top-read',
]
SPOTIFY_CALLBACK_URL = 'http://localhost:5000/callback/spotify'

app = Flask(__name__)
app.secret_key = os.urandom(12)


spotify_api_config = {
    'SPOTIFY_CLIENT_ID': os.environ.get('SPOTIFY_CLIENT_ID'),
    'SPOTIFY_CLIENT_SECRET': os.environ.get('SPOTIFY_CLIENT_SECRET'),
    'SPOTIFY_CALLBACK_URL': os.environ.get('SPOTIFY_CALLBACK_URL') or SPOTIFY_CALLBACK_URL,
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.before_first_request
def load_spotify_api():
    global spotify_api
    spotify_api = SpotifyAuthAPI(
        assign_token=False, config=spotify_api_config, scopes_list=SCOPES
    )

@app.route('/test')
@login_required
def welcome():
    return jsonify(spotify_api.get("me"))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
@login_required
def index():
    return render_template('main.html')


@app.route('/authorize/spotify')
def spotify_authorize():
    authorize_url = spotify_api.get_authorize_url()

    return redirect(authorize_url)


@app.route('/callback/spotify')
def spotify_callback():
    auth_code = request.args['code']

    token = spotify_api.get_access_token(auth_code)
    spotify_api.assign_token(token=token)

    session['logged_in'] = True

    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False

    return redirect(url_for('login'))
