from gtts import gTTS
import os

def text_to_speech(text, lang='en', output_file='output.mp3'):
    # Convert text to speech
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)
    
    # Play the audio file (works on most systems)
    if os.name == 'nt':  # For Windows
        os.system(f'start {output_file}')
    elif os.name == 'posix':  # For macOS/Linux
        os.system(f'open {output_file}' if 'darwin' in os.sys.platform else f'xdg-open {output_file}')

# Example usage
if __name__ == '__main__':
    text = "this fucking song is amazing"
    text_to_speech(text)
