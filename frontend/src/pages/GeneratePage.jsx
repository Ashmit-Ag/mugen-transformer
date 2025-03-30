import React, { useState } from "react";
import api from "../api";
import MusicPlayer from "../components/MusicPlayer";

const GeneratePage = () => {
  const [selectedOption, setSelectedOption] = useState("");
  const moods = ["Cheerful", "Sorrow", "Up Lifting", "Dark"];
  const [isShow, setIsShow] = useState(!!localStorage.getItem("audioSrc")); // Show MusicPlayer if audio exists
  const userId = "1235"; 

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!selectedOption) {
      alert("Please select a mood first");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      localStorage.removeItem("audioSrc"); // Clear old audio

      const response = await api.post(
        `/${userId}/generate-song`,
        { mood: selectedOption, song_number: 5 },
        { responseType: "blob", timeout: 500000 }
      );

      setIsLoading(false);
      const data = await response.data;
      const audioUrl = URL.createObjectURL(data);
      localStorage.setItem("audioSrc", audioUrl);
      setIsShow(true); // Show MusicPlayer
    } catch (error) {
      setIsLoading(false);
      console.error(error);
      setError("An error occurred while generating the song.");
      alert("An error occurred while generating the song.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
      <h1 className="sm:text-6xl md:text-6xl lg:text-7xl text-5xl font-bold mb-8">
        Generate Music
      </h1>
      <p className="text-lg mb-9">Choose a mood to create your track.</p>

      <div className="w-full max-w-md">
        <label className="block text-lg mb-2">Select mood</label>
        <select
          value={selectedOption}
          onChange={(e) => setSelectedOption(e.target.value)}
          className="w-full px-4 py-2 mb-4 bg-gray-800 text-white border border-gray-700 rounded-lg cursor-pointer"
        >
          <option value="" disabled>
            Choose a mood
          </option>
          {moods.map((mood) => (
            <option key={mood} value={mood}>
              {mood}
            </option>
          ))}
        </select>

        <button
          onClick={handleGenerate}
          disabled={isLoading}
          className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
        >
          {isLoading ? "Generating..." : "Generate"}
        </button>

        {/* Loading Spinner */}
        {!isShow && isLoading && (
          <div className="flex flex-col gap-4 mt-4 w-full items-center justify-center">
            <div className="w-20 h-20 border-4 border-transparent animate-spin border-t-blue-500 rounded-full">
              <div className="w-16 h-16 border-4 border-transparent animate-spin border-t-purple-500 rounded-full"></div>
            </div>
          </div>
        )}
      </div>

      {/* Show Music Player if audio is generated */}
      {isShow && <MusicPlayer />}
    </div>
  );
};

export default GeneratePage;
