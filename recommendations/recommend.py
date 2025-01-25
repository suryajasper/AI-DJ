from .schema import Song, Artist
from .llm import GPT
from .utils import extract_list_from_query
from .prompt import Prompt

class RecommendationPipeline:
    def __init__(self):
        self.song_history: list[Song] = []
        self.current_song: Song = None
        self.playlist: list[Song] = []
        self.favorite_artists: list[Artist] = []
        self.llm = GPT()
    
    def add_to_playlist(self, song_title: str):
        song = Song()
        song.artist = Artist()
        song.title = song_title
        self.playlist.append(song)
    
    def remove_from_playlist(self, song_title: str):
        _, index = extract_list_from_query(song_title, [song.title for song in self.playlist])
        self.playlist.pop(index)
    
    def add_artist_to_favorites(self, artist_name: str):
        artist = Artist()
        artist.name = artist_name
        self.favorite_artists.append(artist)
    
    def remove_artist_from_favorites(self, artist_name: str):
        _, index = extract_list_from_query(artist_name, [artist.name for artist in self.favorite_artists])
        self.favorite_artists.pop(index)

    def process_request(self, request: str):
        action_select_prompt = Prompt('select_action')
        action_select_prompt.fill_data({
            'USER_REQUEST': request,
            'SONG_DESCRIPTION': self.current_song.stringify_current(),
        })
        self.llm.request('You are an AI Music DJ', action_select_prompt.get_content())