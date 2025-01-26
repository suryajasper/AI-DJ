from recommendations.schema import Song, Artist
from dotenv import load_dotenv
import requests
import os
import base64
import json

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
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

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

token = get_token()
#print(token)

def search_song(song_name, token, artist_name=None):
    query = f"track:{song_name}"
    if artist_name:
        query += f" artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    headers = get_auth_header(token)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": response.content}
    json_results = response.json()
    return json_results.get("tracks", {}).get("items", [None])[0]


def search_artist(artist_name, token):
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    headers = get_auth_header(token)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": response.content}
    json_results = response.json()
    return json_results.get("artists", {}).get("items", [])[0]

def populate_song_schema(song_data):
    """
    Populate the song schema using data from Spotify.
    """
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

def get_songs(song_names, token, artist_name=None) -> list[Song]:
    if isinstance(song_names, str):
        song_names = [song_names]
    results: list[Song] = []
    for song_name in song_names:
        try:
            song_data = search_song(song_name, token, artist_name)
            if not song_data:
                print('shit')
                results.append(None)
                continue
            results.append(fill_song_schema(song_data))

        except Exception as e:
            print(e)
            results.append(None)
    return results


def fill_song_schema(song_data) -> Song:
    artist_data = song_data["artists"][0]
    artist_id = artist_data.get("id", "")
    artist_name = artist_data.get("name", "")
    artist_details = search_artist(artist_name, token)
    artist_genres = artist_details.get("genres", []) if artist_details else []

    artist = Artist(
        name=artist_data.get("name", ""),
        artist_profile_url=artist_data.get("external_urls", {}).get("spotify", ""),
        artist_genres= artist_genres,
    )
    return Song(
        title=song_data.get("name", ""),
        album_cover_url=song_data.get("album", {}).get("images", [{}])[0].get("url", ""),
        artist=artist,
        album_name=song_data.get("album", {}).get("name", ""),
        song_genres= artist_genres,
        song_moods=[],
        user_reaction=''
    )

def get_artists(artist_names, token):
    if isinstance(artist_names, str):
        artist_names = [artist_names]
    results = []
    for artist_name in artist_names:
        artist_data = search_artist(artist_name, token)
        if not artist_data or "error" in artist_data:
            results.append({"error": f"Artist '{artist_name}' not found."})
        else:
            results.append(fill_artist_schema(artist_data))
    return results

def fill_artist_schema(artist_data):
    return Artist(
        name=artist_data.get("name", ""),
        artist_profile_url=artist_data.get("images", [{}])[0].get("url", ""),
        artist_genres=artist_data.get("genres", [])
    )

try:
    token = get_token()
    artist_list = ["Ed Sheeran", "The Weeknd", "Queen"]
    artists = get_artists(artist_list, token)
    print("Artists Details:", artists)
except Exception as e:
    print(e)




