# OAuth2Util
Utility that allows for easier handling of OAuth2 with PRAW.

In your code you can use it like this:

	import praw
	import OAuth2Util
	
	r = praw.Reddit("Useragent")
	o = OAuth2Util.OAuth2Util(r)

That's it! To refresh the token (it is only valid for one hour), use `o.refresh()`. This checks first whether the token is still valid and doesn't request a new one if it is still valid. So you can call this method befor every block of PRAW usage. Example:

	import time
	while True:
		o.refresh()
		print(r.get_me().comment_karma)
		time.sleep(3600)

If you want to have different tokens (e.g if your script has to log in with different users), you have to specify at least a different oauthtoken config file.

## Reddit Config
In order to use OAuth2, you have to create an App on Reddit (https://www.reddit.com/prefs/apps/). For most use cases you will choose `script` as app type. You have to set the `redirect uri` to `http://127.0.0.1:65010/authorize_callback`, the other fields are up to you.

## Config
OAuth2Util uses three config files to store the information. You can specify the name of them when you create the Util. Before you can use it, you have to fill out the first two, the third one will be filled out.

### OAuthAppInfo
Contains the client id and client secret of the app.

	thisistheid
	ThisIsTheSecretDoNotShare

### OAuthConfig
Contains the requested scopes (separated by one `,`) and whether a refreshable token should be used.

	identity,read
	True

### OAuthToken
Contains the token and the refresh token. This config file is maintained by OAuth2Util, you don't have to do anything with it. If it shouldn't work anymore, just delete this file to request new tokens.

	VerySecretToken
	VerySecretRefreshToken