from .recommend import RecommendationPipeline

if __name__ == '__main__':
    rec_pipe = RecommendationPipeline()
    while True:
        user_request = input('>> ')
        if user_request == 'q':
            exit()
        elif user_request == 'current song':
            print(rec_pipe.current_song.stringify_current())
        elif user_request == 'playlist':
            print('\n'.join([song.stringify_past() for song in rec_pipe.playlist]))
        else:
            rec_pipe.process_request(user_request)