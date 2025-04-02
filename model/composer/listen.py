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
        "-c", "10",
        midi_file,
        "-F", output_wav,
        "-r", "44100"  # Sample rate
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful! WAV file saved at: {output_wav}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


files = ['atmospheric_composition', 'epic_composition', 'phonk_composition', 'standard_composition', 'cellular_automaton/drums']

selected =  files[2] #files[1] 'simple_drum'
selected2 = files[3]

midi_file = f'{selected}.mid' 
sf2_file = "../Sound Fonts/OmegaGMGS2.sf2" 
output_wav = f"out/{selected}2.wav"  
# midi_to_wav(midi_file, sf2_file, output_wav)

midi_file = f'{selected2}.mid' 
sf2_file = "../Sound Fonts/OmegaGMGS2.sf2" 
output_wav = f"out/{selected2}2.wav"  

# midi_to_wav(midi_file, sf2_file, output_wav)
