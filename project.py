import spotipy
import spotipy.util as util
import sys
import re
import pprint
from youtube_api import YouTubeDataAPI


yt_api = 'YOUR_YT_API_KEY'
yt = YouTubeDataAPI(yt_api)
print("Succesfully authed with YouTube")

playlist_name = ''
playl = yt.get_videos_from_playlist_id("INSERT_PLAYLIST_ID")
yt_ids = []


for each in playl:
	yt_ids.append(each['video_id'])

video_titles = []
for each in yt_ids:
	
	dali = yt.get_video_metadata(each)
	if dali:
		video_titles.append(dali['video_title'])


#Sanitize - remove () and []
#final = []
#for each in video_titles:
#	result = re.sub(r'\([^)]*\)', '', each)
#	final.append(result)



#Strip video_title and return video name only ( no artist )
#for each in final:
#	i = 0
#	for letter in each:
#		if letter!="-":
#			i+=1
#		else:
#			print(each[2-len(each)+i:])
#			break


#SPOTI API
username = "YOUR_SPOTIFY_USERNAME"
client_id = 'SPOTIFY_CLIENT_ID'
client_secret = 'SPOTIFY_CLIENT_SECRET'
redirect_uri='http://localhost:9090'
scope = 'user-library-read playlist-modify-public'

debuf = []
playlist_id = ""
user_id = ""


token = util.prompt_for_user_token(username,
					scope,
					client_id,
					client_secret,
					redirect_uri)
results_tids = []					
if token:
	print("Succesfully authed with Spotify")
	sp = spotipy.Spotify(auth=token)
	user_id = sp.me()['id']
	sp.trace=False
	res = sp.user_playlist_create(user_id, 'YouTube2Spoti Generated')
	playlist_id = res['uri']
	print("Playlist created")
	print("Adding songs..")

	for each in video_titles:
		result = sp.search(each)
		if(len(result['tracks']['items'])<1):
			print("the song + "+ each + "couldnt be found !")
			debuf.append(each)
		else:
			link = result['tracks']['items'][0]
			results_tids.append(link['uri'])


	print(results_tids)
	


	sp.user_playlist_add_tracks(user_id,playlist_id,results_tids)

	#Failed songs output

	with open("failed_songs.txt","w",encoding="utf-8") as f:
		for each in debuf:
			f.write("%s\n" % each)
	print("Please re-add these songs " + str(debuf))
else:
	print("CANT GET TOKEN FOR ME")

sys.exit(0)



