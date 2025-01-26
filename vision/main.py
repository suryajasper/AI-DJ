import cv2
import numpy as np
import mediapipe as mp
from deepface import DeepFace
import os

class MoodAnalyzer:
    def __init__(self):
        # My Mediapipe 
        self.mp_face = mp.solutions.face_detection
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        # My detectors
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.5) 
        self.pose_detection = self.mp_pose.Pose(min_detection_confidence=0.5)
                                                            # holds past pose landmarks
        self.previous_pose_landmarks = None

    def analyze_emotions(self, frame):                      # From Face
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

            distance = np.sqrt(                                 #  Euclidean distance: corresponding landmarks
                (current_landmark.x - previous_landmark.x) ** 2 +
                (current_landmark.y - previous_landmark.y) ** 2 +
                (current_landmark.z - previous_landmark.z) ** 2
            )
            motion_rate += distance
        self.previous_pose_landmarks = current_landmarks        # Updates previous landmark
        return motion_rate / len(current_landmarks.landmark)    # Normalizing motion rate (Basic math)
    def process_frame(self, frame):                            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      # Converting to RGB          
        emotion = self.analyze_emotions(frame)                  # Detect emotions
        pose_results = self.pose_detection.process(rgb_frame)   # Detect body pose
                                                                # Calculate motion rate
        motion_rate = self.calculate_motion_rate(pose_results.pose_landmarks) if pose_results.pose_landmarks else 0
                                                                # Display results on the frame
        display_text = f"Emotion: {emotion} | Motion Rate: {motion_rate:.2f}"
        cv2.putText(frame, display_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return frame, emotion, motion_rate

def main():
    mood_analyzer = MoodAnalyzer()
    print('initialized mood analysis')
    cap = cv2.VideoCapture(0)
    print("hi")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        processed_frame, emotion, motion_rate = mood_analyzer.process_frame(frame)

        cv2.imshow("AI Emotion & Motion Tracker", processed_frame)
        print(f"Detected Emotion: {emotion} | Motion Rate: {motion_rate:.2f}")

        key = cv2.waitKey(50) & 0xFF
        if key == ord('q'):                                       # q to quit   
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()