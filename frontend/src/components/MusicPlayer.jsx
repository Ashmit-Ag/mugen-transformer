import React, { useEffect, useRef, useState } from "react";

const MusicPlayer = () => {
  const canvasRef = useRef(null);
  const audioRef = useRef(null);
  const [audioCtx, setAudioCtx] = useState(null);
  const [analyser, setAnalyser] = useState(null);
  const [source, setSource] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const audio = new Audio();
    audio.src = URL.createObjectURL(file);
    audio.controls = true;
    audioRef.current = audio;
    document.body.appendChild(audio);

    const context = new (window.AudioContext || window.webkitAudioContext)();
    const analyserNode = context.createAnalyser();
    analyserNode.fftSize = 256;

    const sourceNode = context.createMediaElementSource(audio);
    sourceNode.connect(analyserNode);
    analyserNode.connect(context.destination);

    setAudioCtx(context);
    setAnalyser(analyserNode);
    setSource(sourceNode);
  };

  useEffect(() => {
    if (audioCtx && analyser && source) {
      visualize();
    }
  }, [audioCtx, analyser, source]);

  const visualize = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    canvas.width = window.innerWidth * 0.9;
    canvas.height = 300;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const barWidth = (canvas.width / bufferLength) * 2.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = dataArray[i] / 2;
        ctx.fillStyle = `rgb(${barHeight + 100}, 50, 200)`;
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }
    };
    draw();
  };

  return (
    <div
      style={{
        textAlign: "center",
        background: "black",
        color: "white",
        padding: "20px",
      }}
    >
      <h1>Audio Visualizer</h1>
      <input type="file" accept="audio/*" onChange={handleFileChange} />
      <canvas
        ref={canvasRef}
        style={{ display: "block", margin: "20px auto", background: "#222" }}
      ></canvas>
    </div>
  );
};

export default MusicPlayer;
