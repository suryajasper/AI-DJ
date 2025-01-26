from vision import MoodAnalyzer
from speech_analysis.speech_to_text import SpeechToTextLoop
from recommendations.recommend import RecommendationPipeline
import cv2
import json
import asyncio
import websockets
from queue import Queue
from threading import Thread
from time import sleep

# Shared queue for communication
request_queue = asyncio.Queue()

async def websocket_handler(websocket):
    """ Handles incoming WebSocket connections and requests """
    print('WebSocket connection established')
    
    try:
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            print(f"Received user request: {message}")

            # Add user request to queue for processing
            await request_queue.put((websocket, message))
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed.")

async def run_recommendation_engine():
    """ Processes user requests and sends back recommendations """
    rec_pipe = RecommendationPipeline()
    
    while True:
        websocket, recv_packet = await request_queue.get()  # Wait for new request
        
        print('Received', recv_packet)
        
        if 'type' in recv_packet and recv_packet['type'] == 'user_request':
            print("Processing user request...")
            user_request = recv_packet['content']
            packets_to_send = rec_pipe.process_request(user_request)

            for packet in packets_to_send:
                await websocket.send(json.dumps(packet))
            print(f"Sent {len(packets_to_send)} actions to frontend")

async def start_websocket_server():
    """ Start WebSocket server """
    print('Starting WebSocket server...')
    async with websockets.serve(websocket_handler, "localhost", 5298):
        await asyncio.Future()  # Keeps server running indefinitely

def run_face_recognition(queue):
    """ Captures video feed and processes face recognition & mood detection """
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

def main():
    queue = Queue()

    # Run face recognition in a separate thread
    # face_thread = Thread(target=run_face_recognition, args=(queue,), daemon=True)
    # face_thread.start()

    # Run the WebSocket server & recommendation engine in an asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    websocket_server = start_websocket_server()
    recommendation_task = run_recommendation_engine()

    loop.run_until_complete(asyncio.gather(websocket_server, recommendation_task))

if __name__ == "__main__":
    main()
