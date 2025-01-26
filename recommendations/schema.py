from pydantic import BaseModel

class SpeedRating(BaseModel):
    rating: int

class Action(BaseModel):
    index: int
    action: str
    user_request: str
    data: str

class ActionList(BaseModel):
    actions: list[Action]

class SongRecommendation(BaseModel):
    song_title: str
    artist_name: str
    response: str

class SongRecommendationList(BaseModel):
    song_recs: list[SongRecommendation]

class Artist(BaseModel):
    name: str
    artist_profile_url: str
    artist_genres: list[str]

class Song(BaseModel):
    id: str
    preview_url: str
    title: str
    album_cover_url: str
    artist: Artist
    album_name: str
    song_genres: list[str]
    song_moods: list[str]
    user_reaction: str

    def stringify_past(self) -> str:
        return (
            f'Song "{self.title}" by {self.artist.name} -- user reacted, "{self.user_reaction}"'
        )
    
    def stringify_current(self) -> str:
        return (
            f'- Title: {self.title} \n'
            f'- Artist Name: {self.artist.name} \n'
            f'- Artist Genres: {",".join(self.artist.artist_genres)} \n'
            f'- Album Name: {self.album_name} \n'
            f'- Genres: {",".join(self.song_genres)} \n'
            f'- Moods: {",".join(self.song_moods)} \n'
        )