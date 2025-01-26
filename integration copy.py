from vision import MoodAnalyzer
from speech_analysis.speech_to_text import SpeechToTextLoop
from recommendations.recommend import RecommendationPipeline
import cv2
import json
from queue import Queue
from threading import Thread
from time import sleep
import websockets
import asyncio

def run_face_recognition(queue):
    mood_analyzer = MoodAnalyzer()
    cap = cv2.VideoCapture(0)
    transcription = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        
        if not queue.empty():
            data = queue.get()
            transcription = data.get('data', '')
        
        processed_frame, emotion, motion_rate = mood_analyzer.process_frame(frame)

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

def run_recommendation_engine():
    rec_pipe = RecommendationPipeline()
    while True:
        user_request = "GET FROM WEBSOCKET"
        packets_to_send = rec_pipe.process_request(user_request)

async def websocket_handler(websocket):
    print('WebSocket connection established')
    while True:
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
            message = json.loads(message)
            print(f"Received: {message}")
        except asyncio.TimeoutError:
            pass

def start_websocket_server():
    print('Starting WebSocket server')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = websockets.serve(
        lambda ws, path: websocket_handler(ws, path), "localhost", 5298
    )

    loop.run_until_complete(server)
    loop.run_forever()

# Main function to run both concurrently
def main():
    queue = Queue()

    # face_thread = Thread(target=run_face_recognition, args=(queue,), daemon=True)
    websocket_thread = Thread(target=start_websocket_server, args=(), daemon=True)

    # face_thread.start()
    websocket_thread.start()

    print("Both models are running. Press 'q' to quit the face recognition window.")

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping models...")


if __name__ == "__main__":
    main()
