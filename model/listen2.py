import subprocess
import os

def midi_to_audio(midi_file, sf2_file, output_wav, output_mp3=None, gain=2.0, target_wav_size=15):
    """
    Convert a MIDI file to WAV and optionally MP3 while keeping the WAV file under a target size.
    
    :param midi_file: Path to the input MIDI file.
    :param sf2_file: Path to the SoundFont (.sf2) file.
    :param output_wav: Path to the output WAV file.
    :param output_mp3: Path to the output MP3 file (optional).
    :param gain: Gain adjustment for volume.
    :param target_wav_size: Max WAV file size in MB.
    """
    # Determine sample rate based on file size constraint
    sample_rate = "44100"
    bit_depth = "16"
    
    if target_wav_size <= 15:
        sample_rate = "32000"  # Lower sample rate to reduce size
    if target_wav_size <= 10:
        sample_rate = "22050"  # Further reduction
        bit_depth = "8"  # Reduce bit depth for smaller size
    
    # Generate WAV file with optimized settings
    command = [
        "fluidsynth",
        "-ni", sf2_file,
        "-c", "10",
        "-z", "4096",
        "-g", str(gain),
        midi_file,
        "-F", output_wav,
        "-r", sample_rate
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Conversion successful! WAV file saved at: {output_wav}")
        
        # Check file size and reduce further if necessary
        wav_size_mb = os.path.getsize(output_wav) / (1024 * 1024)  # Convert bytes to MB
        print(f"Generated WAV file size: {wav_size_mb:.2f} MB")
        
        if wav_size_mb > target_wav_size:
            print("WAV file is too large. Compressing to MP3 only...")
            output_mp3 = output_mp3 or output_wav.replace(".wav", ".mp3")  # Auto-set MP3 name
        
        # Convert to MP3
        if output_mp3:
            ffmpeg_command = [
                "ffmpeg",
                "-y",
                "-i", output_wav,
                "-b:a", "192k",  # Set bitrate to keep quality while reducing size
                output_mp3
            ]
            subprocess.run(ffmpeg_command, check=True)
            print(f"MP3 conversion successful! MP3 file saved at: {output_mp3}")
            
            # If WAV is too large, delete it and keep MP3 only
            if wav_size_mb > target_wav_size:
                os.remove(output_wav)
                print(f"WAV file deleted, keeping only MP3: {output_mp3}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Example usage
# midi_to_audio("input.mid", "soundfont.sf2", "output.wav", "output.mp3")
