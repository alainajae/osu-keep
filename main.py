import flask
import requests

# import environment variables from .env
import dotenv
dotenv.load_dotenv()

import os

app = flask.Flask(__name__)

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

@app.route('/')
def root():
   return flask.redirect("/static/index.html", code=302)

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

@app.route('/getscores')
def get_scores():
    user_key = flask.request.args['user_key_field']
    user = get_user(user_key)
    user_id = user['id']

    params = {
        'include_fails': 1,
        'limit': 1
    }

    response = requests.get(f'{API_URL}/users/{user_id}/scores/best', params=params, headers=HEADERS)
    user_scores = response.json()

    return flask.Response(f'{user_scores}', mimetype='text/html') # cast json to string with default python formatting then pass to Response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)