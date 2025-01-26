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
        if song.id in [old_song.id for old_song in self.playlist]:
            return
        self.history[-1].user_reaction = 'User liked this'
        self.playlist.append(song)
    
    def remove_song_from_playlist(self, song_title: str):
        full_title, index = extract_list_from_query(song_title, [song.title for song in self.playlist])
        print(f'Removing "{full_title}" from playlist')
        self.playlist.pop(index)
    
    def add_artist_to_favorites(self, artist: Artist):
        print(f'Adding artist {artist.name} to favorites')
        if artist.name in [old_artist.name for old_artist in self.favorite_artists]:
            return
        self.favorite_artists.append(artist)
    
    def remove_artist_from_favorites(self, artist_name: str):
        full_name, index = extract_list_from_query(artist_name, [artist.name for artist in self.favorite_artists])
        print(f'Removing artist {full_name} from favorites')
        self.favorite_artists.pop(index)

    def recommend_song(self, request: str) -> tuple[Song, str]:
        previous_songs = '\n'.join([
            f'- {song.stringify_past()}' for song in self.history
        ])
        new_song_prompt = Prompt('new_song', data={
            'USER_REQUEST': request,
            'SONG_LIST': previous_songs,
            'CURRENT_SONG_DESCRIPTION': self.get_current_song_desc(),
        })
        with open('shit.txt', 'w') as out:
            out.write(new_song_prompt.get_content())
            
        response = self.llm.request('You are an AI Music DJ', new_song_prompt.get_content(), output_schema=SongRecommendationList)
        best_song: SongRecommendation = response['song_recs'][0]
        
        found_song = False
        try:
            new_song = search_song(best_song.song_title, best_song.artist_name)
            new_song.user_reaction = 'User is neutral about this'
            self.history.append(new_song)
            self.current_song = new_song 
            print(best_song.response)
            return self.current_song, best_song.response

        except Exception as e:
            print(f'Could not find song "{best_song.song_title}" by {best_song.artist_name}')
            return self.recommend_song(request)      
    
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

    def process_request(self, request: str) -> list[dict]:
        action_select_prompt = Prompt('select_action', data={
            'USER_REQUEST': request,
            'SONG_DESCRIPTION': self.get_current_song_desc(),
        })
        response = self.llm.request('You are an AI Music DJ', action_select_prompt.get_content(), output_schema=ActionList)
        actions : list[Action] = response['actions']
        packets = []
        for action in actions:
            print('Performing action', action)
            action_id = action.index
            if action_id == 1:
                self.add_artist_to_favorites(self.current_song.artist)
                packets.append({
                    'type': 'refresh_artists',
                    'content': [artist.model_dump() for artist in self.favorite_artists[::-1]]
                })
            # elif action_id == 2:
                # self.remove_artist_from_favorites(action.data)
            elif action_id == 3:
                self.add_song_to_playlist(self.current_song)
                packets.append({
                    'type': 'refresh_songs',
                    'content': [song.model_dump() for song in self.playlist[::-1]]
                })
            # elif action_id == 4:
            #     self.remove_song_from_playlist(action.data)
            elif action_id == 5:
                new_song, dj_response = self.recommend_song(action.user_request)
                print(new_song.stringify_current())
                packets.extend([
                    {
                        'type': 'change_song',
                        'content': new_song.model_dump()
                    },
                    {
                        'type': 'dj_response',
                        'content': dj_response
                    }
                ])
            elif action_id == 6:
                answer = self.answer_question(action.user_request)
                print(answer)
                packets.append({
                    'type': 'dj_response',
                    'content': answer
                })
            elif action_id == 7:
                answer = self.handle_miscellaneous(action.user_request)
                print(answer)
                packets.append({
                    'type': 'dj_response',
                    'content': answer
                })
        return packets
