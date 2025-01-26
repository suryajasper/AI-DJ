export interface IArtist {
    name: string;
    artist_profile_url: string;
    artist_genres: string[];
}

export interface ISong {
    id: string;
    preview_url: string;
    title: string;
    album_cover_url: string;
    artist: IArtist;
    album_name: string;
    song_genres: string[];
    song_moods: string[];
    user_reaction: string;
}