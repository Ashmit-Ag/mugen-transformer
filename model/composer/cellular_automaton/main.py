import mido
from mido import MidiFile, MidiTrack, Message
from drum_generator import CellularAutomatonDrums

# MIDI Configuration
BPM = 120  # Set tempo
TICKS_PER_BEAT = 480  # Standard resolution
MIDI_DRUM_CHANNEL = 9  # Drums are on channel 9



def create_midi(drum_pattern, filename):
    """
    Converts a drum pattern into a MIDI file.

    Args:
        drum_pattern (list): List of MIDI note tuples (pitch, velocity, start_time, duration).
        filename (str): The output MIDI filename.
    """
    midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    midi.tracks.append(track)

    # Set Tempo (Prevent Slow Playback)
    tempo = mido.bpm2tempo(BPM)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    current_time = 0  # Running time in ticks

    for pitch, velocity, start_time, duration in drum_pattern:
        # Convert start time and duration to MIDI ticks
        time_delta = max(0, int(start_time * TICKS_PER_BEAT) - current_time)
        current_time += time_delta  # Update running time

        # Shorten note duration to avoid slow playback
        note_duration = int(duration * TICKS_PER_BEAT * 0.2)  # Reduce by 80%

        # Drum notes (Use Channel 9)
        track.append(Message('note_on', note=pitch, velocity=velocity, time=time_delta, channel=MIDI_DRUM_CHANNEL))
        track.append(Message('note_off', note=pitch, velocity=0, time=note_duration, channel=MIDI_DRUM_CHANNEL))

    midi.save(filename)
    print(f"✅ MIDI file saved as {filename}")


# STEP 1: Generate Simple Drums (4 bars)
simple_drums = CellularAutomatonDrums(bars=4, beats_per_bar=4, complexity=0.4, is_phonk=False)
for _ in range(4):
    simple_drums.evolve_simple()

# STEP 2: Generate Complex Drums (4 bars, based on Simple Drums)
complex_drums = CellularAutomatonDrums(bars=4, beats_per_bar=4, complexity=0.7, is_phonk=True, base_pattern=simple_drums.grid)
for _ in range(4):
    complex_drums.evolve_complex()

# STEP 3: Merge Simple & Complex Drums into One Track
final_pattern = simple_drums.get_pattern() + complex_drums.get_pattern()

# STEP 4: Save to MIDI
create_midi(final_pattern, "drums.mid")
