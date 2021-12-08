from email.utils import parseaddr
import flask
import requests
import comment
import logindata
import hashlib
import logging
import objects

# import environment variables from .env
import dotenv
dotenv.load_dotenv()

import os
if (os.path.exists("./osu-keep-b226a1b1acf3.json")):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "./osu-keep-b226a1b1acf3.json"

app = flask.Flask(__name__)

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

@app.route('/')
@app.route('/index.html')
def root():
   return flask.render_template('index.html')

@app.route('/aboutus.html')
def about_page():
   return flask.render_template('aboutus.html')

@app.route('/login.html')
def login_page():
   return flask.render_template('login.html')

@app.route('/createaccount.html')
def account_create_page():
   return flask.render_template('createaccount.html')

@app.route('/dologin', methods=['POST'])
def dosignin():
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    passwordhash = get_password_hash(password)
    user = logindata.load_user(username, passwordhash)
    if user:
        flask.session['user'] = user.username
        return flask.redirect('/')
    else:
        return show_login_page()

@app.route('/signout')
def signout():
    flask.session['user'] = None
    return flask.redirect('/')

@app.route('/docreateaccount', methods=['POST'])
def register_user():
    username = flask.request.form.get('username')
    password1 = flask.request.form.get('password1')
    password2 = flask.request.form.get('password2')
    email = flask.request.form.get('email')
    errors = []
    if password1 != password2:
        errors.append('Passwords do not match.')
    email_parts = parseaddr(email)
    if len(email_parts) != 2 or not email_parts[1]:
        errors.append('Invalid email address: ' + str(email))

    user = objects.User(username, email)
    if errors:
        return show_page('/createaccount.html', 'Sign Up', errors=errors)
    else:
        passwordhash = get_password_hash(password1)
        logindata.save_user(user, passwordhash)
        flask.session['user'] = user.username
        return flask.redirect('/')

@app.route('/about')
def about():
    user = get_user()
    if user:
        about = lmsdatastore.load_about_user(user)
        return show_page('about.html', 'Edit Info for ' + user, text=about)
    return show_login_page()

@app.route('/saveabout', methods=['POST'])
def saveabout():
    user = get_user()
    if user:
        about = flask.request.form.get('about')
        lmsdatastore.save_about_user(user, about)
        return flask.redirect('/user/' + user)
    return show_login_page()


def get_password_hash(pw):
    """This will give us a hashed password that will be extremlely difficult to
    reverse.  Creating this as a separate function allows us to perform this
    operation consistently every time we use it."""

    encoded = pw.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def get_user():
    """If our session has an identified user (i.e., a user is signed in), then
    return that username."""

    return flask.session.get('user', None)


def show_login_page():
    errors = ['You are not signed in.']
    return show_page('/signin.html', 'Sign In', errors)

def show_page(page, title, courses=None, course=None, lesson=None,
              completions=None, show=True, text=None, lines=None, errors=None):
    return flask.render_template(page,
                                 page_title=title,
                                 user=get_user(),
                                 courses=courses,
                                 course=course,
                                 lesson=lesson,
                                 show=show,
                                 completions=completions,
                                 text=text,
                                 lines=lines,
                                 errors=errors)

def get_token():
   data = {
      'client_id': os.getenv("OSU-CLIENT-ID"),
      'client_secret': os.getenv("OSU-CLIENT-SECRET"),
      'grant_type': 'client_credentials',
      'scope': 'public'
   }

   response = requests.post(TOKEN_URL, data=data)

   return response.json().get('access_token')

TOKEN = get_token()
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {TOKEN}'
} 

def get_user(user_key):
    """
    Returns a User object which extends UserCompact from a user key which can be a username or user ID
    """
    params = {
        'key': {user_key}
    }
    
    response = requests.get(f'{API_URL}/users/{user_key}', params=params, headers=HEADERS)
    return response.json()

@app.route('/get-comments', methods=['GET'])
def get_comments():
    """
    Gets comments list and returns it as JSON
    """
    return flask.jsonify(comment.get_comments_list())

@app.route('/create-comment', methods=['POST'])
def handle_create_comment():
    """
    Creates a comment from the given POST request and returns a comment list
    """
    comment_message = flask.request.get_json(silent=True)['message']
    comment.create_comment('user', comment_message) # TODO: replace 'user' with current logged in user
    return get_comments()

@app.route('/get-scores', methods=['GET'])
def get_scores():
    """
    Requests user scores from osu API using given User ID in request header and returns best 100 scores by pp
    """
    user_id = flask.request.headers.get('user-id')
    params = {
        'include_fails': 1,
        'limit': 100
    }

    response = requests.get(f'{API_URL}/users/{user_id}/scores/best', params=params, headers=HEADERS)
    user_scores = response.json() # this is not actually a json its just a python list
    return flask.jsonify(user_scores)
    
@app.route('/get-profile')
def get_profile():
    """
    Render profile page from given username or user ID
    """
    user_key = flask.request.args['user']    
    user = get_user(user_key)
    user_id = user['id']
    username = user['username']
    return flask.render_template('profile.html', user_id=user_id, username = username)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)