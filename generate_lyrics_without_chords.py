# data is from a json file, with the following structure (songs.json):
# {
#     "songs": [
#         {
#             "id": 1,
#             "title": "song title",
#             "lang": "language",
#             "lyrics": "song lyrics",
#             "language_links": []
#         },
#         {
#             "id": 2,
#             "title": "song title",,
#             "lang": "language",
#             "lyrics": "song lyrics",
#             "language_links": []
#         }
#     ]
# }
# there are other fields in the json file, but they are not used in this script (e.g. books instead of songs)
# lyrics looks like this (with chords): 
# "Father [D]Abraham\nHas many [A7]sons\nMany sons has father [D]Abraham\nI am one of them and so are [G]you\nSo [D]let's go [A7]marching [D]on\n\n  Left foot… (Repeat)\n  []Right foot\n  []Left arm\n  []Right arm\n  []Nod your head\n  []Turn around\n  []Sit Down!"
# the goal is to remove the chords, so the lyrics look like this (and add as a new field in the json file):
# "Father Abraham\nHas many sons\nMany sons has father Abraham\nI am one of them and so are you\nSo let's go marching on\n\n  Left foot… (Repeat)\n  Right foot\n  Left arm\n  Right arm\n

import json
import re

# load data from songs.json
songs_json = json.loads(open("songs.json", encoding="utf-8").read())
songs = songs_json["songs"]

# remove chords from lyrics
for song in songs:
    song["lyrics_without_chords"] = re.sub(r"\[.*?\]", "", song["lyrics"])

# save data to songs.json
with open("songs_updated.json", "w") as f:
    json.dump(songs_json, f, indent=4)
