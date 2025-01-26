import cv2
import numpy as np
import mediapipe as mp
from deepface import DeepFace
import speech_recognition as sr
import whisper
import torch
from queue import Queue
from threading import Thread
from time import sleep
import os


# Define the Speech-to-Text class
class SpeechToTextLoop:
    def __init__(self, queue, model='tiny.en', energy_threshold=600, record_timeout=2, phrase_timeout=20):
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


# Define the MoodAnalyzer class
class MoodAnalyzer:
    def __init__(self):
        # My Mediapipe 
        self.mp_face = mp.solutions.face_detection
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        # My detectors
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.5) 
        self.pose_detection = self.mp_pose.Pose(min_detection_confidence=0.5)
        self.previous_pose_landmarks = None

    def analyze_emotions(self, frame):                      
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = rgb_frame[y:y + h, x:x + w]
            try:
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                dominant_emotion = result[0]['dominant_emotion']
                return dominant_emotion
            except Exception:
                continue
        
        return "neutral"

    def calculate_motion_rate(self, current_landmarks): 
        if not current_landmarks or self.previous_pose_landmarks is None:
            self.previous_pose_landmarks = current_landmarks
            return 0 

        motion_rate = 0
        for i, current_landmark in enumerate(current_landmarks.landmark):
            previous_landmark = self.previous_pose_landmarks.landmark[i]

            distance = np.sqrt(                                
                (current_landmark.x - previous_landmark.x) ** 2 +
                (current_landmark.y - previous_landmark.y) ** 2 +
                (current_landmark.z - previous_landmark.z) ** 2
            )
            motion_rate += distance
        self.previous_pose_landmarks = current_landmarks
        return motion_rate / len(current_landmarks.landmark)

    def process_frame(self, frame):                            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)         
        emotion = self.analyze_emotions(frame)                 
        pose_results = self.pose_detection.process(rgb_frame)   
                                                                
        motion_rate = self.calculate_motion_rate(pose_results.pose_landmarks) if pose_results.pose_landmarks else 0
        display_text = f"Emotion: {emotion} | Motion Rate: {motion_rate:.2f}"
        cv2.putText(frame, display_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return frame, emotion, motion_rate


# Function to run face recognition
def run_face_recognition(queue):
    mood_analyzer = MoodAnalyzer()
    cap = cv2.VideoCapture(0)
    transcription = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Check for new transcription in the queue
        if not queue.empty():
            data = queue.get()
            transcription = data.get('data', '')

        # Process the frame
        processed_frame, emotion, motion_rate = mood_analyzer.process_frame(frame)

        # Overlay transcription on the frame
        cv2.putText(
            processed_frame,
            f"Speech: {transcription}",
            (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.imshow("AI Emotion & Motion Tracker", processed_frame)
        print(f"Emotion: {emotion}, Motion Rate: {motion_rate:.2f}, Speech: {transcription}")

        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Function to run speech-to-text
def run_speech_to_text(queue):
    stt = SpeechToTextLoop(queue)
    stt.transcribe_audio()


# Main function to run both concurrently
def main():
    queue = Queue()

    # Start threads for face recognition and speech-to-text
    face_thread = Thread(target=run_face_recognition, args=(queue,), daemon=True)
    stt_thread = Thread(target=run_speech_to_text, args=(queue,), daemon=True)

    face_thread.start()
    stt_thread.start()

    print("Both models are running. Press 'q' to quit the face recognition window.")

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping models...")


if __name__ == "__main__":
    main()
