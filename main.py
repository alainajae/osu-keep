import flask
import requests
import comment

# import environment variables from .env
import dotenv
dotenv.load_dotenv()

import os
if (os.path.exists("./osu-keep-b226a1b1acf3.json")):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "./osu-keep-b226a1b1acf3.json"

app = flask.Flask(__name__)

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

current_scores = {}
current_comments = {}

comment_section = comment.CommentSection()

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

def request_scores(user_id):
    """
    Requests user scores from osu API and stores in global variable
    """
    params = {
        'include_fails': 1,
        'limit': 1
    }

    response = requests.get(f'{API_URL}/users/{user_id}/scores/best', params=params, headers=HEADERS)
    user_scores = response.json() # this is not actually a json its just a python list
    scores_json = flask.jsonify(user_scores)
    global current_scores
    current_scores = scores_json

@app.route('/get-comments', methods=['GET'])
def get_comments():
    global current_comments
    current_comments = flask.jsonify(comment_section.get_comments_list())
    return current_comments

@app.route('/create-comment', methods=['POST'])
def handle_create_comment():
    """
    Creates a comment and returns a comment list
    """
    comment_message = flask.request.get_json(silent=True)['message']
    comment_section.create_comment('user', comment_message) # TODO: replace 'user' with current logged in user
    return get_comments()

@app.route('/get-scores', methods=['GET'])
def get_scores_data():
    return current_scores
    
@app.route('/get-profile')
def get_profile():
    user_key = flask.request.args['user']    
    user = get_user(user_key)
    user_id = user['id']
    request_scores(user_id)
    return flask.render_template('profile.html', user=user_key)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)