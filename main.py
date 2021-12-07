import flask
import requests
import comment
import login as authentication
import api as API
from functools import wraps

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
   login = get_login_info()
   return flask.render_template('index.html', login= login)

@app.route('/aboutus.html')
def about_page():
   return flask.render_template('aboutus.html')

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if session['user_name'] is None:
				return redirect( url_for( 'page_unauthorized' ) )
		except Exception as e:
			return redirect( url_for( 'page_unauthorized' ) )
		return f(*args, **kwargs)
	return decorated_function

def get_login_info():
	try:
		return {
			'user_name': session['user_name'],
			'user_id': session['user_id'],
			'logged_in': True
		}
	except:
		pass

	return {
		'user_name': "",
		'user_id': "",
		'logged_in': False
	}


@app.route( '/login/', methods = ['GET'] )
def login():
	auth = authentication.Auth()
	return flask.redirect( auth.request_auth())

@app.route( '/callback/' )
def callback():

	state = request.args.get( 'state' )

	if state == OAUTH_STATE:
		auth = authentication.Auth()
		code = request.args.get( 'code' )
		user = auth.authorize( code )
		api = API.Osuapi(user)

		me = API.get_me()
		session['user_name'] = str( me['username'] )
		session['user_id'] = str( me['id'] )

	return flask.redirect('/')


""" logout user """
@app.route( '/logout/' )
@login_required
def logout():
	session.pop( 'user_name', None )
	session.pop( 'user_id', None )
	return redirect( '/' )


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