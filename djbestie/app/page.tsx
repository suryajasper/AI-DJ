"use client";
import 'regenerator-runtime/runtime';
import { useEffect, useRef, useState } from "react";
import { Unity, useUnityContext } from "react-unity-webgl";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import { ISong, IArtist } from "./types";

const sendSocket = new WebSocket("ws://localhost:5298");
let socketSend = (data: any) => {};
let addDjResponse = (message: string) => {};
let setPlaylistGlobal = (songs: ISong[]) => {};
let setFavoritesGlobal = (artists: IArtist[]) => {};
let changeSong = (song: ISong, rating: number) => {};

sendSocket.addEventListener("open", (event) => {
  console.log("send socket is open");
  sendSocket.send(JSON.stringify({ status: "up and running" }));
  socketSend = (packet) => {
    console.log("sending packet", packet);
    sendSocket.send(JSON.stringify(packet));
  };
});

sendSocket.addEventListener("message", (event) => {
  console.log(`Message from send socket: ${event.data}`);
  let data = JSON.parse(event.data);
  if (data.type == "dj_response") {
    addDjResponse(data.content);
  }
  else if (data.type == "refresh_songs") {
    setPlaylistGlobal(data.content as ISong[]);
  }
  else if (data.type == "refresh_artists") {
    setFavoritesGlobal(data.content as IArtist[]);
  }
  else if (data.type == "change_song") {
    changeSong(data.content.song as ISong, data.content.speed_rating);
  }
});

function getRandomInt(min: number, max: number) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

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
        const barHeight = (dataArray[i]) / 2 + 6;
    
        // Create a dynamic color that shifts through the hue spectrum
        const hue = (i * 360) / bufferLength; // Distribute hues across the spectrum
        const saturation = 80;  // Saturation (80% for vivid colors)
        const lightness = 50;   // Lightness (50% for a balanced brightness)
        
        // Set the color using HSL
        ctx.fillStyle = `#c9a0ff`;
    
        const center = canvas.height / 2;
        const barY = center - barHeight / 2; // Oscillating between top and bottom
    
        ctx.beginPath();
    
        // Top curve
        ctx.arc(
          x + barWidth / 2, // X position (center of the bar)
          barY,             // Y position (top of the bar)
          barWidth / 2,     // Radius for top curve
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
          barWidth / 2,     // Radius for bottom curve
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

  const fakeArtist: IArtist = {
    name: "Echo Reverie",
    artist_profile_url: "/coverImgs/sabrina.jpg",
    artist_genres: ["Dream Pop", "Shoegaze", "Indie Rock"]
  };
  const fakeSong: ISong = {
    id: "song12345",
    preview_url: "/track.mp3",
    title: "Waves of Midnight",
    album_cover_url: "/coverImgs/sabrina.jpg",
    artist: fakeArtist,
    album_name: "Celestial Echoes",
    song_genres: ["Dream Pop", "Indie Rock"],
    song_moods: ["Ethereal", "Melancholic", "Uplifting"],
    user_reaction: "Loved it! Perfect for a late-night drive."
  };

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [visualTime, setVisualTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentSong, setCurrentSong] = useState<ISong>(fakeSong);

  const [playlist, setPlaylist] = useState<ISong[]>([]);
  const [favoriteArtists, setFavoriteArtists] = useState<IArtist[]>([]);

  const [isMuted, setMuted] = useState(true);
  const [djMessage, setDjMessage] = useState("");

  addDjResponse = (message: string) => {
    setDjMessage(message.slice(0, 250));
  };
  setPlaylistGlobal = (newPlaylist: ISong[]) => {
    setPlaylist(newPlaylist);
  };
  setFavoritesGlobal = (newFavorites: IArtist[]) => {
    setFavoriteArtists(newFavorites);
  };
  changeSong = (song: ISong, rating: number) => {
    sendMessage('GameController', 'setSpeed', rating);
    sendMessage('GameController', 'pickUpRecord');
    setCurrentSong(song);

    if (audioRef.current) {
      audioRef.current.src = song.preview_url;
      audioRef.current.load();
      audioRef.current.play().catch(error => console.error("Playback error:", error));
      audioRef.current.currentTime = 0;
    }
  };

  useEffect(() => {
    let duration = 274;
    setDuration(duration);
    setVisualTime(Math.random() * (duration - 30));
  }, [currentSong]);

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
      let deltaTime = audio.currentTime - currentTime;
      setCurrentTime(audio.currentTime);
      if (deltaTime > 0) {
        setVisualTime(oldTime => oldTime + deltaTime);
      }
    }
  };

  const handleLoadedMetadata = () => {
    const audio = audioRef.current;
    if (audio) {
      console.log("Metadata loaded - Duration:", audio.duration);
      let duration = 274;
      setDuration(duration);
      setVisualTime(Math.min(0, Math.random() * (duration - audio.duration)));
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60).toString().padStart(2, "0");
    return `${minutes}:${seconds}`;
  };
  
  const { unityProvider, sendMessage } = useUnityContext({
    loaderUrl: "build/Build/build.loader.js",
    dataUrl: "build/Build/build.data",
    frameworkUrl: "build/Build/build.framework.js",
    codeUrl: "build/Build/build.wasm",
  });

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  useEffect(() => {
    if (isMuted) {
      SpeechRecognition.stopListening();
      if (transcript) {
        socketSend({
          type: "user_request",
          content: transcript,
        });
      }
      resetTranscript();
    }
    else {
      resetTranscript();
      setDjMessage("");
      SpeechRecognition.startListening({ continuous: true });
    }
  }, [isMuted])

  return (
    <div className="w-screen h-screen px-[5%] flex justify-center items-center gap-[48px]">
      <div className="w-[60%] h-[80%] justify-between items-center flex flex-col">
        <h1 className="text-center text-[100px] my-[-20px] text-[--popcol]">DJ Bestie</h1>
        <h1 className="text-center text-[30px] font-sans">
          Your AI Music Companion
        </h1>
        <div className="h-[80%] mt-[24px] w-full border-2 border-[--grey1] rounded-[25px] cursor-pointer overflow-hidden relative">
          <Unity unityProvider={unityProvider} style={{ width: "100%", height: "100%" }} />;
        </div>
        <button onClick={() => {setMuted(!isMuted)}}>{isMuted ? "Unmute" : "Mute"}</button>
        <div>
          {(isMuted && djMessage && `DJ: ${djMessage}`) || (transcript && `User: ${transcript}`)}
        </div>
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
                src={currentSong.album_cover_url}
                alt="Cover"
                className="w-[auto] h-[auto] rounded-lg object-cover"
              />
            </div>
            <div className="w-[72%] h-[auto] pl-[24px] flex flex-col justify-center">
              <div className="pb-[12px]">
                <h2 className="text-[1.2vw] font-bold">{currentSong.title}</h2>
                <h3 className="text-[0.9vw] text-[--grey1]">{currentSong.artist.name}</h3>
              </div>


              <div className="flex items-center gap-[12px] w-full">
                <audio
                  autoPlay
                  loop
                  crossOrigin="anonymous"
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
                    className="h-full bg-[--popcol] rounded-full"
                    style={{ width: `${(visualTime / duration) * 100}%` }}
                  ></div>
                </div>
                <span className="text-[0.8vw]">
                  {formatTime(visualTime)} / {formatTime(duration)}
                </span>
              </div>
            </div>

          </div>

          <div className="w-full h-[48%] grid grid-cols-2 gap-[24px]">
            <div className="w-full h-full border-2 border-[--grey1] rounded-[25px] overflow-hidden pr-[4px]">
              <div className="rounded-t-[10px] bg-[--popcol] h-[15%] mr-[-4px] mb-[12px] p-[12px] flex items-center">
                <h1 className="text-[1vw] mx-[auto] text-[--dark2]">Playlist</h1>
              </div>
              <div className="px-[12px] pb-[12px] gap-[12px] h-[82%] flex flex-col overflow-y-scroll">
                {playlist.map((song: ISong) => {
                  return (
                    <div
                      className="w-full min-h-[20%] border-2 border-[--grey1] rounded-[15px] cursor-pointer hover:scale-[1.02] flex"
                      key={song.id}
                    >
                      <div className="w-auto h-full flex flex-col">
                        <img
                          src={song.album_cover_url}
                          alt={song.title}
                          className="w-auto h-full rounded-[10px] object-cover"
                        />
                      </div>
                      <div className="w-[auto] h-full flex flex-col pl-[10px] justify-center">
                        <h2 className="text-[0.85vw] font-medium">{song.title}</h2>
                        <h3 className="text-[0.75vw]">{song.artist.name}</h3>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="w-full h-full border-2 border-[--grey1] rounded-[25px] overflow-hidden pr-[4px]">
              <div className="rounded-t-[10px] bg-[--popcol] h-[15%] mr-[-4px] mb-[12px] p-[12px] flex items-center">
                <h1 className="text-[1vw] mx-[auto] text-[--dark2]">Favorite Artists</h1>
              </div>
              <div className="px-[12px] pb-[12px] gap-[12px] h-[82%] flex flex-col overflow-y-scroll">
                {favoriteArtists.map((artist: IArtist, i) => {
                  return (
                    <div
                      className="w-full min-h-[20%] border-2 border-[--grey1] rounded-[15px] cursor-pointer hover:scale-[1.02] flex"
                      key={i}
                    >
                      <div className="w-auto h-full flex flex-col">
                        <img
                          src={artist.artist_profile_url}
                          alt={artist.name}
                          className="w-auto h-full rounded-[10px] object-cover"
                        />
                      </div>
                      <div className="w-[auto] h-full flex flex-col pl-[10px] justify-center">
                        <h2 className="text-[0.8vw]">{artist.name}</h2>
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
