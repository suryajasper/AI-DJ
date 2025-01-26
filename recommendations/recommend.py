from .schema import *
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
    
    def add_song_to_playlist(self, song: Song):
        self.playlist.append(song)
    
    def remove_song_from_playlist(self, song_title: str):
        _, index = extract_list_from_query(song_title, [song.title for song in self.playlist])
        self.playlist.pop(index)
    
    def add_artist_to_favorites(self, artist: Artist):
        self.favorite_artists.append(artist)
    
    def remove_artist_from_favorites(self, artist_name: str):
        _, index = extract_list_from_query(artist_name, [artist.name for artist in self.favorite_artists])
        self.favorite_artists.pop(index)

    def recommend_song(self, request: str):
        previous_songs = '\n'.join([
            f'- {song.stringify_past()}' for song in self.playlist
        ])
        new_song_prompt = Prompt('new_song', data={
            'USER_REQUEST': request,
            'SONG_LIST': previous_songs,
            'CURRENT_SONG_DESCRIPTION': self.current_song.stringify_current()
        })
        response: SongRecommendationList = self.llm.request('You are an AI Music DJ', new_song_prompt.get_content(), output_schema=SongRecommendationList)
        best_song = response.song_recs[0]
        self.add_song_to_playlist(self.current_song)
        self.current_song = Song(title=best_song)
    
    def answer_question(self, request: str) -> str:
        song_question_prompt = Prompt('song_question', data={
            'USER_REQUEST': request,
            'CURRENT_SONG_DESCRIPTION': self.current_song.stringify_current(),
        })
        answer: str = self.llm.request('You are an AI Music DJ', song_question_prompt.get_content())
        return answer

    def handle_miscellaneous(self, request: str) -> str:
        previous_songs = '\n'.join([
            f'- {song.stringify_past()}' for song in self.playlist
        ])
        misc_prompt = Prompt('song_question', data={
            'USER_REQUEST': request,
            'SONG_LIST': previous_songs,
            'CURRENT_SONG_DESCRIPTION': self.current_song.stringify_current()
        })
        answer: str = self.llm.request('You are an AI Music DJ', misc_prompt.get_content())
        return answer

    def process_request(self, request: str):
        action_select_prompt = Prompt('select_action', data={
            'USER_REQUEST': request,
            'SONG_DESCRIPTION': self.current_song.stringify_current(),
        })
        response: ActionList = self.llm.request('You are an AI Music DJ', action_select_prompt.get_content(), output_schema=ActionList)
        actions: list[Action] = response.actions
        for action in actions:
            action_id = action.index
            if action_id == 1:
                self.add_artist_to_favorites(self.current_song.artist)
            elif action_id == 2:
                self.remove_artist_from_favorites(action.data)
            elif action_id == 3:
                self.add_song_to_playlist(self.current_song)
            elif action_id == 4:
                self.remove_song_from_playlist(self.current_song.title)
            elif action_id == 5:
                self.recommend_song(action.user_request)
            elif action_id == 6:
                self.answer_question(action.user_request)
            elif action_id == 7:
                self.handle_miscellaneous(action.user_request)
