import praw
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread

# ### CONFIGURATION ### #
REFRESH_MARGIN = 60
REDIRECT_URL = "127.0.0.1"
REDIRECT_PORT = 65010
REDIRECT_PATH = "callback"
# ### END CONFIGURATION ### #

class OAuth2UtilRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		parsed_url = urlparse(self.path)
		
		if parsed_url[2] != "/" + REDIRECT_PATH: # 2 = Path
			self.send_response(404)
			self.end_headers()
			return
		
		parsed_query = parse_qs(parsed_url[4]) # 4 = Query
		
		if not "code" in parsed_query:
			self.send_response(200)
			self.send_header("Content-Type", "text/plain")
			self.end_headers()
			
			self.wfile.write("No code found, try again!".encode("utf-8"))
			return
		
		self.server.oauth2util.response_code = parsed_query["code"][0]
		
		self.send_response(200)
		self.send_header("Content-Type", "text/plain")
		self.end_headers()
		
		self.wfile.write("Thank you for using OAuth2Util. The authorization was successful, you can now close this window.".encode("utf-8"))

class OAuth2Util:

	def __init__(self, reddit, oauthappinfo_configfile = "oauthappinfo.txt", oauthconfig_configfile = "oauthconfig.txt", oauthtoken_configfile = "oauthtoken.txt"):
		self.r = reddit
		self.token = None
		self.refresh_token = None
		self.valid_until = time.time()
		self.scopes = []
		self.refreshable = True
		self.server = None
		
		self.OAUTHAPPINFO_CONFIGFILE = oauthappinfo_configfile
		self.OAUTHCONFIG_CONFIGFILE = oauthconfig_configfile
		self.OAUTHTOKEN_CONFIGFILE = oauthtoken_configfile
		
		self._read_app_info()
		self._read_config()
		self._read_access_credentials()
	
	# ### LOAD SETTINGS ### #
	
	def _read_app_info(self):
		try:
			lines = []
			with open(self.OAUTHAPPINFO_CONFIGFILE, "r") as f:
				for line in f:
					if line.strip():
						lines.append(line.strip())
			self.r.set_oauth_app_info(lines[0], lines[1], "http://{0}:{1}/{2}".format(REDIRECT_URL, REDIRECT_PORT, REDIRECT_PATH))
		except OSError:
			print(self.OAUTHAPPINFO_CONFIGFILE, "not found.")
			
	def _read_config(self):
		try:
			lines = []
			with open(self.OAUTHCONFIG_CONFIGFILE, "r") as f:
				for line in f:
					if line.strip():
						lines.append(line.strip())
			self.scopes = lines[0].split(",")
			self.refreshable = lines[1] == "True"
		except OSError:
			print(self.OAUTHCONFIG_CONFIGFILE, "not found.")
			
	def _read_access_credentials(self):
		try:
			lines = []
			with open(self.OAUTHTOKEN_CONFIGFILE, "r") as f:
				for line in f:
					if line.strip():
						lines.append(line.strip())
			self.token = lines[0]
			self.refresh_token = lines[1]
			self.r.set_access_credentials(set(self.scopes), self.token, self.refresh_token)
		except (OSError,  praw.errors.OAuthInvalidToken):
			print("Request new Token")
			self._get_new_access_information()
			
	# ### SAVE SETTINGS ### #
	
	def _save_token(self):
		with open(self.OAUTHTOKEN_CONFIGFILE, "w") as f:
			f.write("{0}\n{1}\n".format(self.token, self.refresh_token))
			
	# ### REQUEST FIRST TOKEN ### #

	def _start_webserver(self):
		server_address = (REDIRECT_URL, REDIRECT_PORT)
		self.server = HTTPServer(server_address, OAuth2UtilRequestHandler)
		self.server.oauth2util = self
		self.response_code = None
		t = Thread(target=self.server.serve_forever)
		t.deamon = True
		t.start()
	
	def _wait_for_response(self):
		while self.response_code == None:
			time.sleep(2)
		time.sleep(5)
		self.server.shutdown()

	def _get_new_access_information(self):
		self._start_webserver()
		url = self.r.get_authorize_url("SomeRandomState", self.scopes, self.refreshable)
		webbrowser.open(url)
		self._wait_for_response()
		
		try:
			access_information = self.r.get_access_information(self.response_code)
		except praw.errors.OAuthException:
			print("--------------------------------")
			print("Can not authenticate, maybe the app infos (e.g. secret) are wrong.")
			print("--------------------------------")
			raise
		
		self.token = access_information["access_token"]
		self.refresh_token = access_information["refresh_token"]
		self.valid_until = time.time() + 3600
		self._save_token()
		
	# ### REFRESH TOKEN ### #
	
	def set_access_credentials(self):
		"""
		Set the token on the Reddit Object again
		"""
		self.r.set_access_credentials(set(self.scopes), self.token, self.refresh_token)
	
	def refresh(self):
		"""
		Check if the token is still valid and requests a new if it is not valid anymore
		
		Call this method before a call to praw
		if there might have passed more than one hour
		"""
		if time.time() > self.valid_until - REFRESH_MARGIN:
			print("Refresh Token")
			new_token = self.r.refresh_access_information(self.refresh_token)
			self.token = new_token["access_token"]
			self.valid_until = time.time() + 3600
			self._save_token()
			#self.set_access_credentials(self.scopes, self.refreshable)