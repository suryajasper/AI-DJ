"use client";
import { useEffect, useRef } from "react";

export default function Home() {
  const canvasRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const audio = audioRef.current;
    const ctx = canvas.getContext("2d");

    // Set up Web Audio API
    const audioContext = new (window.AudioContext || window.AudioContext)();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256; // Size of the frequency bin (power of 2)
    const bufferLength = 30;
    const dataArray = new Uint8Array(bufferLength);

    // Connect audio element to analyser
    const source = audioContext.createMediaElementSource(audio);
    source.connect(analyser);
    analyser.connect(audioContext.destination);

    // Function to draw the visualizer
    const drawVisualizer = () => {
      requestAnimationFrame(drawVisualizer);

      analyser.getByteFrequencyData(dataArray); // Get frequency data

      ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas

      // Draw frequency bars
      const barWidth = canvas.width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = Math.sqrt(dataArray[i]) * 3.5 + 6;
        const r = 255;
        const g = 255;
        const b = 255;
        ctx.fillStyle = `rgb(${r},${g},${b})`;

        const center = canvas.height / 2;
        const barY = center - barHeight / 2; // Oscillating between top and bottom

        ctx.fillRect(x, barY, barWidth, barHeight);
        x += barWidth + 1;
      }
    };

    // Start drawing when audio is playing
    audio.onplay = () => {
      audioContext.resume().then(() => {
        drawVisualizer();
      });
    };
  }, []);

  useEffect(() => {
    const audio = audioRef.current;

    const timeout = setTimeout(() => {
      if (audio.paused) {
        audio.play();
      }
    }, 500);

    return () => clearTimeout(timeout); // Cleanup timeout on unmount
  }, []);

  return (
    <div className="w-screen h-screen px-[5%] flex justify-center items-center gap-[48px]">
      <div className="w-[60%] h-[80%] justify-between items-center flex flex-col">
        <h1 className="text-center text-[100px] my-[-20px]">DJ Bestie</h1>
        <h1 className="text-center text-[30px] font-sans">
          Your AI Music Player
        </h1>
        <div className="h-[80%] mt-[24px] w-full border-2 border-zinc-700 rounded-[25px]"></div>
      </div>
      <div className="w-[38%] h-full flex flex-col gap-[24px] justify-center items-center">
        <div className="h-[80%] w-full flex flex-col justify-between">
          <div className="w-full h-[20%] border-2 border-zinc-700 rounded-[25px] overflow-hidden">
            <audio ref={audioRef} autoPlay>
              <source src="/track.mp3" type="audio/mp3" />
              Your browser does not support the audio element.
            </audio>
            <canvas
              className="w-full h-full p-[12px] flex justify-center items-center"
              ref={canvasRef}
            ></canvas>
          </div>

          <div className="w-full h-[26%] border-2 border-zinc-700 rounded-[25px]"></div>
          <div className="w-full h-[48%] grid grid-cols-2 gap-[24px]">
            <div className="w-full h-full border-2 border-zinc-700 rounded-[25px] overflow-hidden pr-[4px]">
              <div className="rounded-t-[10px] bg-[--spotify] h-[15%] mr-[-4px] mb-[12px] p-[12px] flex items-center">
                <h1 className="text-[0.85vw] mx-[auto]">Queue</h1>
              </div>
              <div className="px-[12px] pb-[12px] gap-[12px] h-[82%] flex flex-col overflow-y-scroll">
                {[1, 2, 3, 4, 5, 6, 7, 8].map((item: any) => {
                  return (
                    <div
                      className="w-full min-h-[20%] border-2 border-zinc-700 rounded-[15px] cursor-pointer hover:scale-[1.02]"
                      key={item}
                    ></div>
                  );
                })}
              </div>
            </div>
            <div className="w-full h-full border-2 border-zinc-700 rounded-[25px] overflow-hidden pr-[4px]">
              <div className="rounded-t-[10px] bg-[--spotify] h-[15%] mr-[-4px] mb-[12px] p-[12px] flex items-center">
                <h1 className="text-[0.85vw] mx-[auto]">Similar Artists</h1>
              </div>
              <div className="px-[12px] pb-[12px] gap-[12px] h-[82%] flex flex-col overflow-y-scroll">
                {[1, 2, 3, 4, 5, 6, 7, 8].map((item: any) => {
                  return (
                    <div
                      className="w-full min-h-[20%] border-2 border-zinc-700 rounded-[15px] cursor-pointer hover:scale-[1.02]"
                      key={item}
                    ></div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
