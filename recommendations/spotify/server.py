from flask import Flask, request, jsonify
from pymongo import MongoClient
from .spotify import *
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)
token = get_token()
load_dotenv()
password = os.getenv("MONGODB_PASSWORD")

client = MongoClient(f"mongodb+srv://georgemathew9203:{password}@djbestie.cfczo.mongodb.net/?retryWrites=true&w=majority")
db = client.my_database
songs_collection = db.songs
artists_collection = db.artists


@app.route("/add-song", methods = ["POST"])
def add_song():
    request_data = request.json
    song_name = request_data.get("song_name")

    if not song_name:
        return jsonify({"error": "Please provide a song_name in the request body."}), 400
    song_data = search_song(song_name, token)

    if not song_data:
        return jsonify({"error": "Song not found on Spotify."}), 404
    song_document = populate_song_schema(song_data)

    try:
        result = songs_collection.insert_one(song_document)
        return jsonify({"message": "Song added successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": "Failed to add song to the database", "details": str(e)}), 500



@app.route("/add-artist", methods = ["POST"])
def add_artist():
    request_data = request.json
    artist_name = request_data.get("artist_name")

    if not artist_name:
        return jsonify({"error": "Please provide an artist_name in the request body."}), 400
    artist_data = search_artist(artist_name, token)

    if not artist_data:
        return jsonify({"error": "Artist not found on Spotify."}), 404
    artist_document = populate_artist_schema(artist_data)

    try:
        result = artists_collection.insert_one(artist_document)
        return jsonify({"message": "Artist added successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": "Failed to add artist to the database", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)