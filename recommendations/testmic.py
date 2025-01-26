import sounddevice as sd
import numpy as np
import whisper

model = whisper.load_model("base")
print("Whisper model loaded successfully!")

SAMPLE_RATE = 16000
CHUNK_DURATION = 5

def record_and_transcribe():
    print("Listening... Press Ctrl+C to stop.")

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=0, dtype="float32", channels=1) as stream:
            while True:
                audio_chunk, _ = stream.read(int(SAMPLE_RATE * CHUNK_DURATION))
                audio_chunk = np.squeeze(audio_chunk)

                print(f"Audio chunk shape: {audio_chunk.shape}")
                print(f"Audio chunk max value: {np.max(audio_chunk)}")

                if np.max(audio_chunk) < 0.01:
                    print("No significant audio detected. Skipping...")
                    continue
                
                print("Transcribing...")
                result = model.transcribe(audio_chunk, fp16=False)
                print(f"Transcription: {result['text']}")
    except KeyboardInterrupt:
        print("\nStopped listening.")
    except Exception as e:
        print(f"An error occurred: {e}")

record_and_transcribe()
