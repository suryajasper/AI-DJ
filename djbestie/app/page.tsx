"use client";
import { useEffect, useRef, useState } from "react";

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const audio = audioRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    // Set up Web Audio API
    const audioContext = new (window.AudioContext || window.AudioContext)();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256; // Size of the frequency bin (power of 2)
    const bufferLength = 30;
    const dataArray = new Uint8Array(bufferLength);

    // Connect audio element to analyser
    if (audio) {
      const source = audioContext.createMediaElementSource(audio);
      source.connect(analyser);
      analyser.connect(audioContext.destination);
    }

    // Function to draw the visualizer
    const drawVisualizer = () => {
      requestAnimationFrame(drawVisualizer);

      analyser.getByteFrequencyData(dataArray); // Get frequency data

      if (!ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas

      // Draw frequency bars
      const barWidth = canvas.width / (bufferLength + 15);
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = Math.sqrt(dataArray[i]) * 6 + 6;
        const r = 255;
        const g = 255;
        const b = 255;
        ctx.fillStyle = `rgb(${r},${g},${b})`;

        const center = canvas.height / 2;
        const barY = center - barHeight / 2; // Oscillating between top and bottom

        ctx.beginPath();

        // Top curve
        ctx.arc(
          x + barWidth / 2, // X position (center of the bar)
          barY,             // Y position (top of the bar)
          barWidth / 2,           // Radius for top curve
          Math.PI,          // Start angle
          0,                // End angle
          false             // Draw clockwise (top side)
        );

        // Draw the right vertical line
        ctx.lineTo(x + barWidth, barY + barHeight);

        // Bottom curve
        ctx.arc(
          x + barWidth / 2, // X position (center of the bar)
          barY + barHeight, // Y position (bottom of the bar)
          barWidth / 2,           // Radius for bottom curve
          0,                // Start angle (bottom)
          Math.PI,          // End angle (bottom)
          false             // Draw clockwise (bottom side)
        );

        // Draw the left vertical line
        ctx.lineTo(x, barY); // Return to the top

        ctx.closePath();
        ctx.fill();

        x += barWidth + 8;
      }
    };

    // Start drawing when audio is playing
    if (audio) {
      audio.onplay = () => {
        audioContext.resume().then(() => {
          drawVisualizer();
        });
      };
    }
  }, []);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [songTitle, setSongTitle] = useState("Song Title");
  const [artistName, setArtistName] = useState("Artist Name");
  const [coverImg, setCoverImg] = useState("/coverImgs/sabrina.jpg");

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current?.pause();
    } else {
      audioRef.current?.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    const audio = audioRef.current;
    if (audio) {
      setCurrentTime(audio.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    const audio = audioRef.current;
    if (audio) {
      console.log("Metadata loaded - Duration:", audio.duration);
      setDuration(audio.duration);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, "0");
    return `${minutes}:${seconds}`;
  };


  return (
    <div className="w-screen h-screen px-[5%] flex justify-center items-center gap-[48px]">
      <div className="w-[60%] h-[80%] justify-between items-center flex flex-col">
        <h1 className="text-center text-[100px] my-[-20px] text-[--popcol]">DJ Bestie</h1>
        <h1 className="text-center text-[30px] font-sans">
          Your AI Music Companion
        </h1>
        <div className="h-[80%] mt-[24px] w-full border-2 border-[--grey1] rounded-[25px] cursor-pointer hover:scale-[1.02]"></div>
      </div>
      <div className="w-[38%] h-full flex flex-col gap-[24px] justify-center items-center">
        <div className="h-[80%] w-full flex flex-col justify-between">
          <div className="w-full h-[20%] border-2 border-[--grey1] rounded-[25px] overflow-hidden cursor-pointer hover:scale-[1.02]">
            <canvas
              className="w-full h-full p-[12px] flex justify-center items-center"
              ref={canvasRef}
            ></canvas>
          </div>

          <div className="w-full h-[26%] border-2 border-[--grey1] rounded-[25px] cursor-pointer hover:scale-[1.02] flex">
            <div className="w-[25%] flex flex-col justify-center pl-[12px]">
              <img
                src={coverImg}
                alt="Cover"
                className="w-[auto] h-[auto] rounded-lg object-cover"
              />
            </div>
            <div className="w-[72%] h-[auto] pl-[24px] flex flex-col justify-center">
              <div className="pb-[12px]">
                <h2 className="text-[1.2vw] font-bold">{songTitle}</h2>
                <h3 className="text-[0.9vw] text-[--grey1]">{artistName}</h3>
              </div>


              <div className="flex items-center gap-[12px] w-full">
                <audio
                  ref={audioRef}
                  src="/track.mp3"
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                />
                <button
                  className="bg-[--popcol] text-[--grey2] rounded-full p-[4px] hover:scale-110 transition"
                  onClick={togglePlay}
                >
                  {isPlaying ? "⏸️" : "▶️"}
                </button>
                <div className="w-[50%] h-[6px] bg-[--grey2] rounded-full overflow-hidden">
                  <div
                    className="h-[full] bg-[--popcol] rounded-full"
                    style={{ width: `${(currentTime / duration) * 100}%` }}
                  ></div>
                </div>
                <span className="text-[0.8vw]">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </div>
            </div>

          </div>

          <div className="w-full h-[48%] grid grid-cols-2 gap-[24px]">
            <div className="w-full h-full border-2 border-[--grey1] rounded-[25px] overflow-hidden pr-[4px]">
              <div className="rounded-t-[10px] bg-[--popcol] h-[15%] mr-[-4px] mb-[12px] p-[12px] flex items-center">
                <h1 className="text-[1vw] mx-[auto] text-[--dark2]">Similar Songs</h1>
              </div>
              <div className="px-[12px] pb-[12px] gap-[12px] h-[82%] flex flex-col overflow-y-scroll">
                {[
                  { id: 1, cover: "/coverImgs/sabrina.jpg", name: "yeehaw", artist: "Sabrina Carpenter" },
                  { id: 2, cover: "/path/cover.jpg", name: "Song 2", artist: "Artist 2" },
                  { id: 3, cover: "/path/cover.jpg", name: "Song 3", artist: "Artist 3" },
                  { id: 4, cover: "/path/cover.jpg", name: "Song 4", artist: "Artist 4" },
                  { id: 5, cover: "/path/cover.jpg", name: "Song 5", artist: "Artist 5" },
                  { id: 6, cover: "/path/cover.jpg", name: "Song 6", artist: "Artist 6" },
                  { id: 7, cover: "/path/cover.jpg", name: "Song 7", artist: "Artist 7" },
                  { id: 8, cover: "/path/cover.jpg", name: "Song 8", artist: "Artist 8" },
                ].map((item: any) => {
                  return (
                    <div
                      className="w-full min-h-[20%] border-2 border-[--grey1] rounded-[15px] cursor-pointer hover:scale-[1.02] flex"
                      key={item.id}
                    >
                      <div className="w-auto h-full flex flex-col">
                        <img
                          src={item.cover}
                          alt={item.name}
                          className="w-auto h-full rounded-[10px] object-cover"
                        />
                      </div>
                      <div className="w-[auto] h-full flex flex-col pl-[10px] justify-center">
                        <h2 className="text-[0.85vw] font-medium">{item.name}</h2>
                        <h3 className="text-[0.75vw]">{item.artist}</h3>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="w-full h-full border-2 border-[--grey1] rounded-[25px] overflow-hidden pr-[4px]">
              <div className="rounded-t-[10px] bg-[--popcol] h-[15%] mr-[-4px] mb-[12px] p-[12px] flex items-center">
                <h1 className="text-[1vw] mx-[auto] text-[--dark2]">Similar Artists</h1>
              </div>
              <div className="px-[12px] pb-[12px] gap-[12px] h-[82%] flex flex-col overflow-y-scroll">
                {[
                  { id: 1, cover: "/coverImgs/sabrina.jpg", artist: "Sabrina Carpenter" },
                  { id: 2, cover: "/path/cover.jpg", artist: "Artist 2" },
                  { id: 3, cover: "/path/cover.jpg", artist: "Artist 3" },
                  { id: 4, cover: "/path/cover.jpg", artist: "Artist 4" },
                  { id: 5, cover: "/path/cover.jpg", artist: "Artist 5" },
                  { id: 6, cover: "/path/cover.jpg", artist: "Artist 6" },
                  { id: 7, cover: "/path/cover.jpg", artist: "Artist 7" },
                  { id: 8, cover: "/path/cover.jpg", artist: "Artist 8" },
                ].map((item: any) => {
                  return (
                    <div
                      className="w-full min-h-[20%] border-2 border-[--grey1] rounded-[15px] cursor-pointer hover:scale-[1.02] flex"
                      key={item.id}
                    >
                      <div className="w-auto h-full flex flex-col">
                        <img
                          src={item.cover}
                          alt={item.name}
                          className="w-auto h-full rounded-[10px] object-cover"
                        />
                      </div>
                      <div className="w-[auto] h-full flex flex-col pl-[10px] justify-center">
                        <h2 className="text-[0.8vw]">{item.artist}</h2>
                      </div>
                    </div>
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
