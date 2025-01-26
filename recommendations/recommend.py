from .schema import *
from .llm import GPT
from .utils import extract_list_from_query
from .prompt import Prompt
from .spotify.spotify import search_artist, search_song

class RecommendationPipeline:
    def __init__(self):
        self.song_history: list[Song] = []
        self.current_song: Song = None
        self.playlist: list[Song] = []
        self.history: list[Song] = []
        self.favorite_artists: list[Artist] = []
        self.llm = GPT()
    
    def get_current_song_desc(self) -> str:
        return 'No song currently playing' if not self.current_song else self.current_song.stringify_current()

    def add_song_to_playlist(self, song: Song):
        print(f'Adding "{song.title}" by {song.artist} to playlist')
        self.history[-1].user_reaction = 'User liked this'
        self.playlist.append(song)
    
    def remove_song_from_playlist(self, song_title: str):
        full_title, index = extract_list_from_query(song_title, [song.title for song in self.playlist])
        print(f'Removing "{full_title}" from playlist')
        self.playlist.pop(index)
    
    def add_artist_to_favorites(self, artist: Artist):
        print(f'Adding artist {artist.name} to favorites')
        self.favorite_artists.append(artist)
    
    def remove_artist_from_favorites(self, artist_name: str):
        full_name, index = extract_list_from_query(artist_name, [artist.name for artist in self.favorite_artists])
        print(f'Removing artist {full_name} from favorites')
        self.favorite_artists.pop(index)

    def recommend_song(self, request: str) -> Song:
        previous_songs = '\n'.join([
            f'- {song.stringify_past()}' for song in self.history
        ])
        new_song_prompt = Prompt('new_song', data={
            'USER_REQUEST': request,
            'SONG_LIST': previous_songs,
            'CURRENT_SONG_DESCRIPTION': self.get_current_song_desc(),
        })
        response = self.llm.request('You are an AI Music DJ', new_song_prompt.get_content(), output_schema=SongRecommendationList)
        best_song: SongRecommendation = response['song_recs'][0]
        new_song = search_song(best_song.song_title, best_song.artist_name)
        new_song.user_reaction = 'User is neutral about this'
        if new_song:
            self.history.append(new_song)
            self.current_song = new_song
            print(best_song.response)
        else:
            print(f'Could not find song "{best_song.song_title}" by {best_song.artist_name}')
        return self.current_song
    
    def answer_question(self, request: str) -> str:
        song_question_prompt = Prompt('song_question', data={
            'USER_REQUEST': request,
            'CURRENT_SONG_DESCRIPTION': self.get_current_song_desc(),
        })
        answer: str = self.llm.request('You are an AI Music DJ', song_question_prompt.get_content())
        return answer

    def handle_miscellaneous(self, request: str) -> str:
        previous_songs = '\n'.join([
            f'- {song.stringify_past()}' for song in self.history
        ])
        misc_prompt = Prompt('song_question', data={
            'USER_REQUEST': request,
            'SONG_LIST': previous_songs,
            'CURRENT_SONG_DESCRIPTION': self.get_current_song_desc(),
        })
        answer: str = self.llm.request('You are an AI Music DJ', misc_prompt.get_content())
        return answer

    def process_request(self, request: str):
        action_select_prompt = Prompt('select_action', data={
            'USER_REQUEST': request,
            'SONG_DESCRIPTION': self.get_current_song_desc(),
        })
        response = self.llm.request('You are an AI Music DJ', action_select_prompt.get_content(), output_schema=ActionList)
        actions : list[Action] = response['actions']
        for action in actions:
            print('Performing action', action)
            action_id = action.index
            if action_id == 1:
                self.add_artist_to_favorites(self.current_song.artist)
            # elif action_id == 2:
                # self.remove_artist_from_favorites(action.data)
            elif action_id == 3:
                self.add_song_to_playlist(self.current_song)
            # elif action_id == 4:
            #     self.remove_song_from_playlist(action.data)
            elif action_id == 5:
                new_song = self.recommend_song(action.user_request)
                print(new_song.stringify_current())
            elif action_id == 6:
                print(self.answer_question(action.user_request))
            elif action_id == 7:
                print(self.handle_miscellaneous(action.user_request))
