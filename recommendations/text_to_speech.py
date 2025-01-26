from gtts import gTTS
import os

def text_to_speech(text, lang='en', output_file='output.mp3'):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)  
    if os.name == 'nt':
        os.system(f'start {output_file}')
if __name__ == '__main__':
    text = "this fucking song is amazing"
    text_to_speech(text)
