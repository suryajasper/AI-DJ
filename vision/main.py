from . import MoodAnalyzer
import cv2

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