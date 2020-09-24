from flask import Flask
from flask import url_for
from flask import session
from flask import redirect
from flask import request

from authlib.integrations.flask_client import OAuth

import config

app=Flask(__name__)
app.secret_key = config.FN_FLASK_SECRET_KEY
app.config.from_object('config')

config_URL='https://accounts.google.com/.well-known/openid-configuration'
oauth=OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=config_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def is_logged_in():
    user=session.get('user')
    if user:
        return user
    else:
        return False

@app.route('/')
def home():
    if is_logged_in():
        return f'logged in as {is_logged_in()["name"]}<br><a href="/google/logout">logout</a>'
    else:
        return f'you are not logged in<br><a href="/google/login">login</a>'

@app.route('/google/login')
def google_login():
    redirect_uri=config.FN_BASE_URL + url_for('google_auth')
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/logout')
def google_logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/google/auth')
def google_auth():
    session['_google_authlib_state_'] = request.args.get('state')
    session['_google_authlib_redirect_uri_'] = config.FN_BASE_URL + url_for('google_auth')
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['user'] = user
    return redirect('/')

app.run(port=8080)