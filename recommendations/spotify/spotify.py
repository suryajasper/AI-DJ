from recommendations.schema import Song, Artist
from dotenv import load_dotenv
from urllib.parse import urlencode as encode_query
import requests
import os
import base64
import json
from bs4 import BeautifulSoup
from jsonpath_ng import parse
from pymongo import MongoClient

load_dotenv()
spotify_client_id = os.getenv("CLIENT_ID")
spotify_client_secret = os.getenv("CLIENT_SECRET")
mongodb_password = os.getenv("MONGODB_PASSWORD")

client = MongoClient(f"mongodb+srv://georgemathew9203:{mongodb_password}@djbestie.cfczo.mongodb.net/?retryWrites=true&w=majority")
db = client.my_database
songs_collection = db.songs
artists_collection = db.artists

def get_token():
    auth_string = spotify_client_id + ":" + spotify_client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    results = requests.post(url, headers = headers, data = data)
    json_results = json.loads(results.content)
    token = json_results["access_token"]

    return token

spotify_token = get_token()
def get_auth_header():
    return {"Authorization": "Bearer " + spotify_token}


def search_song(song_name, artist_name=None) -> Song:
    print('Requesting song', song_name, 'by', artist_name)
    song_query_str = query = f"track:{song_name}"
    if artist_name:
        song_query_str += f" artist:{artist_name}"
    query = encode_query({
        "q": song_query_str,
        "type": "track",
        "limit": 1
    })
    url = f"https://api.spotify.com/v1/search?{query}"
    headers = get_auth_header()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": response.content}
    json_results = response.json()
    best_result = json_results.get("tracks", {}).get("items", [None])[0]
    if best_result:
        return fill_song_class(best_result)
    else:
        return None


def search_artist(artist_name) -> Artist:
    query = encode_query({
        "q": artist_name,
        "type": "artist",
        "limit": 1
    })
    url = f"https://api.spotify.com/v1/search?{query}"
    headers = get_auth_header()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": response.content}
    json_results = response.json()
    best_result = json_results.get("artists", {}).get("items", [])[0]
    if best_result and not 'error' in best_result:
        return fill_artist_class(best_result)
    else:
        return None

def populate_song_schema(song_data):
    song_name = song_data["name"]
    song_id = song_data["id"]
    artist_name = song_data["artists"][0]["name"]
    preview_url = get_song_preview_url(song_id)
    if "error" in song_data:
        return {"error": "Cannot populate song schema. Song data is invalid."}
    album_cover_url = song_data["album"]["images"][0]["url"]
    title = song_data["name"]
    artist_name = song_data["artists"][0]["name"]
    album_name = song_data["album"]["name"]
    song_genres = []
    song_moods = ["Happy", "Relaxed"]
    user_reaction = "Loved it!"
    song_schema = {
        "id": song_id,
        "preview_url": preview_url,
        "album_cover_url": album_cover_url,
        "title": title,
        "artist_name": artist_name,
        "album_name": album_name,
        "song_genres": song_genres,
        "song_moods": song_moods,
        "user_reaction": user_reaction,
    }
    return song_schema
  
def populate_artist_schema(artist_data):
    if "error" in artist_data:
        return {"error": "Cannot populate artist schema. Artist data is invalid."}
    artist_profile_url = artist_data["images"][0]["url"] if artist_data.get("images") else None
    name = artist_data["name"]
    artist_genre = artist_data.get("genres", [])
    artist_schema = {
        "artist_profile_url": artist_profile_url,
        "name": name,
        "artist_genre": artist_genre,
    }
    return artist_schema

def get_songs(song_names: list[str], artist_name=None) -> list[Song]:
    if isinstance(song_names, str):
        song_names = [song_names]
    results: list[Song] = []
    for song_name in song_names:
        try:
            song = search_song(song_name, artist_name)
            if not song:
                results.append(None)
                continue
            results.append(song)
        except Exception as e:
            print(e)
            results.append(None)
    return results


def fill_song_class(song_data) -> Song:
    song_name = song_data.get("name", "")
    song_id = song_data.get("id", "")
    artist_data = song_data["artists"][0]
    artist_name = artist_data.get("name", "")
    artist = search_artist(artist_name)
    preview_url = get_song_preview_url(song_id)
    return Song(
        id=song_id,
        preview_url=preview_url,
        title=song_data.get("name", ""),
        album_cover_url=song_data.get("album", {}).get("images", [{}])[0].get("url", ""),
        artist=artist,
        album_name=song_data.get("album", {}).get("name", ""),
        song_genres=artist.artist_genres,
        song_moods=[],
        user_reaction=''
    )

def get_artists(artist_names):
    if isinstance(artist_names, str):
        artist_names = [artist_names]
    results = []
    for artist_name in artist_names:
        artist = search_artist(artist_name)
        if not artist:
            results.append({"error": f"Artist '{artist_name}' not found."})
        else:
            results.append(artist)
    return results

def add_song(song_name, artist_name = None):
    song_data = search_song(song_name, spotify_token, artist_name)
    song_schema = populate_song_schema(song_data)
    result = songs_collection.insert_one(song_schema)

def add_artist( artist_name):
    artist_data = search_artist(artist_name, spotify_token)
    artist_schema = populate_artist_schema(artist_data)
    result = artists_collection.insert_one(artist_schema)
    
def delete_song(song_name, artist_name = None):
    query = {"name": song_name}
    if artist_name:
        query["artist"] = artist_name
    result = songs_collection.delete_one(query)

def fill_artist_class(artist_data):
    return Artist(
        name=artist_data.get("name", ""),
        artist_profile_url=artist_data.get("images", [{}])[0].get("url", ""),
        artist_genres=artist_data.get("genres", [])
    )
 
def get_track_id(song_name, artist_name = None):
    query = f"track:{song_name}"
    if artist_name:
        query += f" artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {spotify_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json()
        items = results.get("tracks", {}).get("items", [])
    return items[0].get("id")

def fetch_preview_url(track_id) -> str:
    embed_url = f"https://open.spotify.com/embed/track/{track_id}"
    try:
        response = requests.get(embed_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
            if next_data_script:
                json_data = json.loads(next_data_script.string)
                return json_data["props"]["pageProps"]["state"]["data"]["entity"]["audioPreview"]["url"]
    except Exception as e:
        print(f"Error occurred: {e}")
    return ''

def get_song_preview_url(track_id):
    # track_id = get_track_id(song_name, token, artist_name)
    preview_url = fetch_preview_url(track_id)
    return preview_url

if __name__ == "__main__":
    mock_song_data = {
        "id": "0VjIjW4GlUZAMYd2vXMi3b",
        "name": "Blinding Lights",
        "album": {
            "name": "After Hours",
            "images": [{"url": "https://i.scdn.co/image/ab67616d00001e02c74f42c430637b44e48d6e7c"}]
        },
        "artists": [
            {"name": "The Weeknd", "id": "1Xyo4u8uXC1ZmMpatF05PJ"}
        ]
    }
    try:
        song_object = fill_song_class(mock_song_data)
        print("\nPopulated Song Object:")
        print(song_object)
    except ValueError as e:
        print(f"Error: {e}")
