
const MyMusicPage = () => {
  // const tracks = [
  //   {
  //     id: 1,
  //     title: "Track Title 1",
  //     mood: "Cheerful",
  //     date: "2024-12-01",
  //     audioUrl: "track1.mp3",
  //   },
  //   {
  //     id: 2,
  //     title: "Track Title 2",
  //     mood: "Dark",
  //     date: "2024-12-05",
  //     audioUrl: "track2.mp3",
  //   },
  // ];
  const user = localStorage.getItem('user')
  const tracks = user.song_list || []


  return (
    <div className="homeBackgroundImage min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
      <h1 className="tsm:text-6xl md:text-6xl lg:text-7xl text-5xl font-bold mb-8">My Music</h1>
      <p className="text-lg mb-8">{tracks == [] ? "Here are your saved tracks:": "No Songs"}</p>
      <div className="w-[90%] max-w-2xl">
        {tracks.map((track) => (
          <div
            key={track.id}
            className="flex flex-col sm:flex-row justify-between items-center p-4 mb-4 bg-gray-800 rounded-lg shadow-lg"
          >
            <div className="flex-1 mb-4 sm:mb-0 sm:mr-4">
              <h2 className="text-xl font-semibold">{track.title}</h2>
              <p className="text-lg">Music 1 {track.genre}</p>
              {/* <p className="text-sm text-gray-400">Created on: {track.date}</p> */}
            </div>
            <div className="flex flex-col items-center sm:items-end">
              <audio
                controls
                className="w-full max-w-sm sm:w-auto"
              >
                <source src={`../assets/${track.audioUrl}`} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyMusicPage;