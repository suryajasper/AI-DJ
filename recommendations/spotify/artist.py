from pymongo import MongoClient
artistSchema = {
    "artist_profile_url":str,
    "name":str,
    "artist_genres":list[str]
}