import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util
import sys
import re
import urllib
import pprint
from spotipy.oauth2 import SpotifyClientCredentials


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


def main():
	debuf = []
	results_tids = []
	print(("123").encode('utf8'))
	yt_api = "AIzaSyA6HtnNpJ8W25deLqyTDQ-6-FiyiIjGOo0"
	yt = YouTubeDataAPI(yt_api)
	print(("Succesfully authed with YouTube").encode('utf8'))

	playlist_name = ''
	print(sys.argv[2])
	playl = yt.get_videos_from_playlist_id(sys.argv[2])
	yt_ids = []

	for each in playl:
		yt_ids.append(each['video_id'])

	video_titles = []

	for each in yt_ids:
		dali = yt.get_video_metadata(each)
		if dali:
			video_titles.append(dali['video_title'])

	# SPOTI_API

	username = sys.argv[1]
	client_id = "5967779dfd91475eb775054013737344"
	client_secret = "367eb2c62b754aa4af103347143de6f7"
	redirect_uri = 'http://spoti2yt.herokuapp.com/callback'
	scope = 'user-library-read playlist-modify-public'

	playlist_id = ""
	user_id = ""
	token = util.prompt_for_user_token(username,
									   scope,
									   client_id,
									   client_secret,

									   redirect_uri)
	if token:
		print(("Succesfully authed with Spotify").encode('utf8'))
		sp = spotipy.Spotify(auth=sys.argv[3])
		user_id = sp.me()['id']
		sp.trace = False
		res = sp.user_playlist_create(user_id, 'YouTube2Spoti Generated')
		playlist_id = res['uri']
		print(("Playlist created").encode('utf8'))
		print(("Adding songs..").encode('utf8'))

		for each in video_titles:
			clean_string = sanitize2(each)
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
		print("Please re-add these songs " + str(debuf))

		print("Added")
	else:
		print("CANT GET TOKEN FOR ME")

	sys.exit(0)


main()
