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
      # TODO: use getenv() for id and secret later which needs to be set up in gcloud
      'client_id': os.getenv("OSU-CLIENT-ID"),
      'client_secret': os.getenv("OSU-CLIENT-SECRET"),
      'grant_type': 'client_credentials',
      'scope': 'public'
   }

   response = requests.post(TOKEN_URL, data=data)

   return response.json().get('access_token')

@app.route('/getscores')
def get_scores():
   user_id = flask.request.args['user_id_field']

   token = get_token()

   headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': f'Bearer {token}'
   }

   params = {
      'mode': 'osu',
      'limit': 1 
   }

   response = requests.get(f'{API_URL}/users/{user_id}/scores/best', params=params, headers=headers)

   user_scores = response.json()

   return flask.Response(f'{user_scores}', mimetype='text/html') # cast json to string with default python formatting then pass to Response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)