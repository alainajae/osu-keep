API_BASE_URL = 'https://osu.ppy.sh/api/v2'

class Osuapi():
	"""docstring for api"""
	def __init__( self, user ):
		self.user = dict( user )
		self.url = API_BASE_URL

	def get_me( self ):
		headers = { 'Authorization': 'Bearer ' + self.user['access_token'] }
		response = requests.get( self.url + '/me', headers = headers )
		return response.json()