import subprocess

def midi_to_wav(midi_file, sf2_file, output_wav):
    """
    Convert a MIDI file to WAV using a SoundFont (.sf2) file and FluidSynth.
    
    :param midi_file: Path to the input MIDI file.
    :param sf2_file: Path to the SoundFont (.sf2) file.
    :param output_wav: Path to the output WAV file.
    """
    command = [
        "fluidsynth",
        "-ni", sf2_file,
        midi_file,
        "-F", output_wav,
        "-r", "44100"  # Sample rate
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful! WAV file saved at: {output_wav}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# midi_file = "standard_fixed.mid"  
# sf2_file = "Sound Fonts/Omega.sf2"
# output_wav = "standard_fixed.wav"  
# midi_to_wav(midi_file, sf2_file, output_wav)
