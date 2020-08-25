import spotipy
import spotipy.util as util
from flask import Flask, jsonify, render_template, flash, url_for, Markup
from flask import render_template, redirect, request, session, make_response, session, redirect
from werkzeug.exceptions import HTTPException
from flask_bootstrap import Bootstrap
import logging
import subprocess
import time
import json
from youtube_api import YouTubeDataAPI
import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util
import sys
import re
import urllib
import pprint

TOKEN = []


application = Flask(__name__)

handler = logging.FileHandler('logs.txt')
handler.setLevel(logging.ERROR)
application.logger.addHandler(handler)

boostrap = Bootstrap(application)

application.secret_key = "qwdkqwiodjj12udj12ud"


@application.errorhandler(Exception)
def handle_exceptions(e):
	if e:
		flash("Please check your credentials")
		return render_template("index.html", content=str(e))


@application.route("/")
def verify():
	sp_auth = spotipy.oauth2.SpotifyOAuth(client_id="5967779dfd91475eb775054013737344",
										  client_secret="367eb2c62b754aa4af103347143de6f7",
										  redirect_uri='http://spoti2yt.herokuapp.com/callback',
										  cache_path="/var/tmp",
										  scope='user-library-read playlist-modify-public')
	auth_url = sp_auth.get_authorize_url()
	print(auth_url)
	print("1")
	session.clear()
	print(request.args)

	return redirect(auth_url)


@application.route("/index")
def init():
	return render_template("index.html")


@application.route("/callback")
def callback():
	sp_auth = spotipy.oauth2.SpotifyOAuth(client_id="5967779dfd91475eb775054013737344",
										  client_secret="367eb2c62b754aa4af103347143de6f7",
										  redirect_uri='http://spoti2yt.herokuapp.com/callback',
										  cache_path="/var/tmp",
										  scope='user-library-read playlist-modify-public')
	code = request.args.get('code')
	print(code)
	token_info = sp_auth.get_access_token(code)
	session["token_info"] = token_info
	print(session["token_info"])
	return render_template("index.html")


@application.route("/go", methods=['POST'])
def go():
	session['token_info'], authorized = get_token(session)
	session.modified = True
	if not authorized:
		return render_template("index.html")
	info = request.form
	# sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
	# print(sp)
	# response = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
	spoti = info['spoti']
	link = info['yt_link']
	x = link.find("list=")
	aauth = session.get('token_info').get('access_token')
	print(link[x+5::])

	debuf = []
	results_tids = []
	print(("123").encode('utf8'))
	yt_api = "AIzaSyA6HtnNpJ8W25deLqyTDQ-6-FiyiIjGOo0"
	yt = YouTubeDataAPI(yt_api)
	print(("Succesfully authed with YouTube").encode('utf8'))

	playlist_name = ''
	playl = yt.get_videos_from_playlist_id(link[x+5::])
	yt_ids = []

	if not playl:
		raise Exception("Check youtube link pls ty")
	else:
		for each in playl:
			yt_ids.append(each['video_id'])

	video_titles = []

	for each in yt_ids:
		dali = yt.get_video_metadata(each)
		if dali:
			video_titles.append(dali['video_title'])


	if authorized:

		token = aauth
		print(("Succesfully authed with Spotify").encode('utf8'))
		sp = spotipy.Spotify(auth=token)

		user_id = sp.me()['id']
		print(user_id)
		if (user_id != spoti):
			raise Exception("Please check your Spotify username and try again.")
		sp.trace = False
		res = sp.user_playlist_create(user_id, 'YouTube2Spoti Generated')
		playlist_id = res['uri']
		print(("Playlist created").encode('utf8'))
		print(("Adding songs..").encode('utf8'))

		for each in video_titles:
			old_clean_string = sanitize2(each)
			clean_string = old_clean_string[:old_clean_string.index('ft.')]
			print((clean_string).encode('utf8'))
			if(clean_string != ""):
				result = sp.search(clean_string)
				if(len(result['tracks']['items']) < 1):
					print(("the song + " + str(clean_string) +
						   " couldnt be found !").encode('utf8'))
					debuf.append(clean_string)
				else:
					link = result['tracks']['items'][0]
					results_tids.append(link['uri'])

		while results_tids:
			sp.user_playlist_add_tracks(
				user_id, playlist_id, results_tids[:100], position=None)
			results_tids = results_tids[100:]
		# Failed songs output

		with open("failed_songs.txt", "w", encoding="utf-8") as f:
			for each in debuf:
				f.write("%s\n" % each)
				each += "<br>"
		print("Please re-add these songs " + str(debuf))
		text = Markup("Success, check Spotify.<br> Please re-add these songs:<br><br>")
		return render_template("index.html", content=text, songs=debuf)
	#fin = f"python3 project.py {spoti} {link[x+5::]} {aauth}"
	#res = subprocess.check_output(fin, shell=True)
	# print(json.dumps(response))
def sanitize2(string2):
	result_brace = re.sub(r'[\(\[].*?[\)\]]', '', string2)
	res2 = result_brace
	final_bate = ""
	i = 0
	while not (res2[i].isalpha()):
		i += 1
		# artist to title tuples
	try:
		result = re.match(r'^(.*?)\s-\s(.*?)$', res2[i:]).groups()
		neznam = result[0].split()
		final_bate += neznam[-1] + " " + result[1]

	except:
		print(("This song is questionnable?" + res2[i:]).encode('utf8'))

	return final_bate


# Checks to see if token is valid and gets a new token if not
def get_token(session):
	token_valid = False
	token_info = session.get("token_info", {})

	# Checking if the session already has a token stored
	if not (session.get('token_info', False)):
		token_valid = False
		return token_info, token_valid

	# Checking if token has expired
	now = int(time.time())
	is_token_expired = session.get('token_info').get('expires_at') - now < 60

	# Refreshing token if it has expired
	if (is_token_expired):
		# Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
		sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id="5967779dfd91475eb775054013737344",
											   client_secret="367eb2c62b754aa4af103347143de6f7",
											   redirect_uri='http://spoti2yt.herokuapp.com/callback',
											   cache_path="/var/tmp/",
											   scope='user-library-read playlist-modify-public')
		token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

	token_valid = True
	return token_info, token_valid


if __name__ == "__main__":
	application.run(debug=True)
