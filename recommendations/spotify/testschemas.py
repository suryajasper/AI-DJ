from pymongo import MongoClient
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("MONGODB_PASSWORD")

client = MongoClient(f"mongodb+srv://georgemathew9203:{password}@djbestie.cfczo.mongodb.net/?retryWrites=true&w=majority")
db = client.my_database
songs_collection = db.songs
artists_collection = db.artists

test_song = {
    "album_cover": "https://example.com/cover.jpg",
    "title": "Shape of You",
    "artist_name": "Ed Sheeran",
    "album_name": "Divide",
    "song_genres": ["Pop", "Acoustic"],
    "song_moods": ["Happy", "Romantic"]
}

# try:

#     # Insert the song into MongoDB
#     result = songs_collection.insert_one(test_song)
#     print(f"Song added to database with ID: {result.inserted_id}")

# except (ValueError, TypeError) as e:
#     print(f"Validation error: {e}")

# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     # Close the connection
#     client.close()

test_artist = {
    "artist_profile_url": "https://example.com/profile.jpg",
    "name": "Ed Sheeran",
    "artist_genre": ["Pop", "Acoustic"]
}

try:
    result = artists_collection.insert_one(test_artist)
    print(f"Artist added to database with ID: {result.inserted_id}")

except (ValueError, TypeError) as e:
    print(f"Validation error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client.close()

