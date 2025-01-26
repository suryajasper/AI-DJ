from pymongo import MongoClient
songSchema = {
    "album_cover_url":str,
    "title":str,
    "artist_name":str,
    "album_name":str,
    "song_genres":list[str],
    "song_moods":list[str],
    "user_reaction":str
}