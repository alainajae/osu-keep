import flask
import requests
import comment
import login as authentication
import api as API
from functools import wraps
from authlib.integrations.flask_client import OAuth

# import environment variables from .env
import dotenv
dotenv.load_dotenv()

import os
if (os.path.exists("./osu-keep-b226a1b1acf3.json")):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "./osu-keep-b226a1b1acf3.json"

app = flask.Flask(__name__)
app.secret_key =  os.urandom(12).hex()


API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'
AUTH_URL = 'https://osu.ppy.sh/oauth/authorize'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

oauth = OAuth(app)
oauth.register(
    name = 'osu',
    client_id= os.getenv("OSU_CLIENT_ID"),
    client_secret= os.getenv("OSU_CLIENT_SECRET"),
    access_token_url = TOKEN_URL, 
    access_token_params=None,
    authorize_url= AUTH_URL,
    authorize_params=None,
    api_base_url=API_URL

)


@app.route('/')

@app.route('/index.html')
def root():
   return flask.render_template('index.html')

@app.route('/aboutus.html')
def about_page():
   return flask.render_template('aboutus.html')

@app.route('/login/')
def login():
    osu = oauth.create_client('osu')  
    redirect_uri = flask.url_for('authorize', _external=True)
    return osu.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    osu = oauth.create_client('osu')  # create the google oauth client
    token = osu.authorize_access_token()  # Access token from google (needed to get user info)
    resp = osu.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.osu.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

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
    user_id = flask.request.headers.get('user_id')
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