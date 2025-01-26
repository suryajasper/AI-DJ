import numpy as np
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from time import sleep

class SpeechToTextLoop:
    def __init__(self, queue, model='tiny.en', energy_threshold=600, record_timeout=1, phrase_timeout=5):
        self.queue = queue
        self.phrase_time = None
        self.data_queue = Queue()
        self.transcription = []

        print("Loading Whisper model...")
        self.audio_model = whisper.load_model(model)
        print("Model loaded successfully!")

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        self.source = sr.Microphone(sample_rate=16000)

        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

        def record_callback(_, audio: sr.AudioData):
            data = audio.get_raw_data()
            self.data_queue.put(data)

        self.recorder.listen_in_background(
            self.source, record_callback, phrase_time_limit=record_timeout
        )

    def transcribe_audio(self):
        while True:
            if not self.data_queue.empty():
                audio_data = b''.join(self.data_queue.queue)
                self.data_queue.queue.clear()

                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                if np.max(audio_np) < 0.01:
                    print("Skipping silent audio...")
                    continue

                result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available(), language="en")
                text = result['text'].strip()
                print(f"Transcription: {text}")
                self.queue.put({'source': 'audio', 'data': text})

    def start_loop(self):
        transcription_thread = Thread(target=self.transcribe_audio, daemon=True)
        transcription_thread.start()

        print("Listening... Press Ctrl+C to stop.")
        try:
            while True:
                sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping transcription loop...")

if __name__ == "__main__":
    queue = Queue()
    stt = SpeechToTextLoop(queue)
    stt.start_loop()
