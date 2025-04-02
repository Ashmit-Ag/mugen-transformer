"""
Main music generator module for the procedural music generation system.
Provides functions for generating complete musical compositions.
"""

import os
import json
import mido
from .midi_utils import create_midi_file_from_notes, transpose_melody, adjust_velocity, repeat_pattern, analyze_melody_octave, get_pattern_length_ticks, fix_note_timings, TICKS_PER_BEAT
from .melody_generator import create_background_melody, create_catchy_secondary_melody
from .harmony_generator import generate_bass_line, generate_chord_progression
from .rhythm_generator import generate_drum_pattern, generate_trap_fill
from .song_structure import generate_song_structure, apply_song_structure
from .audio_effects import apply_reverb, apply_chorus, apply_delay, apply_filter, apply_distortion, apply_filter_sweep
from .music_theory import get_scale_notes, MAJOR_SCALE, MINOR_SCALE

# Channel assignments
DRUM_CHANNEL = 9
BASS_CHANNEL = 2
CHORD_CHANNEL = 1
MELODY_CHANNEL = 0
BG_MELODY_CHANNEL = 3
SECONDARY_MELODY_CHANNEL = 4
SECONDARY_BG_MELODY_CHANNEL = 5
SECONDARY_BASS_CHANNEL = 6
SECONDARY_DRUM_CHANNEL = 10

# Program assignments
CELESTA = 8
ORGAN = 17
HARP = 46
CHOIR = 53
SYNTH_VOICE = 54
HALO_PAD = 94


script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "instruments.json")

def load_instruments():
    """Load instrument definitions from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

def set_instrument_program(track, program, channel):
    """Set the instrument program for a channel."""
    track.append(mido.Message('program_change', program=program, channel=channel, time=0))

def generate_full_composition(
    melody, 
    root_note, 
    scale_type, 
    tempo, 
    output_file, 
    style='trap',
    is_phonk=False,
    is_epic=False,
    is_atmospheric=False,
    is_minimal=False,
    has_breakdown=True,
    num_bars=44
):
    """Generate a full composition with proper song structure and transitions."""
    # Load instruments
    instruments = load_instruments()
    
    # Determine time signature and beats per bar
    beats_per_bar = 4 
    
    # Calculate number of bars based on melody length
    if melody:
        max_time = max(time for _, _, time, _ in melody)
        ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
        melody_bars = (max_time // ticks_per_bar) + 1
    else:
        melody_bars = 4  # Default if no melody provided
    
    # Get scale notes
    scale = get_scale_notes(root_note, scale_type)
    
    # Analyze melody octave to determine secondary melody octave
    avg_octave = analyze_melody_octave(melody)
    
    # Create secondary melody (transposed version)
    if avg_octave >= 5:  # If melody is high, transpose down
        octave_shift = -1
    else:  # If melody is low, transpose up
        octave_shift = 1
    
    secondary_melody = transpose_melody(melody, octave_shift)
    
    # Adjust velocities
    if octave_shift > 0:
        # Original melody is lower, make it quieter
        melody = adjust_velocity(melody, 1.2)
        secondary_melody = adjust_velocity(secondary_melody, 0.8)
    else:
        # Original melody is higher, keep it louder
        melody = adjust_velocity(melody, 1.0)
        secondary_melody = adjust_velocity(secondary_melody, 0.7)
    
    # Create catchy secondary melody (1 bar long)
    catchy_melody = create_catchy_secondary_melody(scale, root_note)
    
    # Create background melodies
    bg_melody = create_background_melody(melody, scale)
    bg_melody_high = transpose_melody(bg_melody, 1)
    bg_melody_low = transpose_melody(bg_melody, -1)
    
    # Generate bass lines
    bass_line = generate_bass_line(root_note, scale_type, melody_bars, beats_per_bar, 0.5, False)
    funky_bass = generate_bass_line(root_note, scale_type, melody_bars, beats_per_bar, 0.7, True)
    
    # Generate chord progression
    chord_progression = generate_chord_progression(root_note, scale_type, melody_bars, beats_per_bar)
    
    # Generate drum patterns
    simple_drums = generate_drum_pattern(melody_bars, beats_per_bar, 0.4, False)
    complex_drums = generate_drum_pattern(melody_bars, beats_per_bar, 0.7, is_phonk)
    
    # Generate a trap fill for transitions
    # trap_fill = generate_trap_fill(2, beats_per_bar, 0.8)
    
    # Calculate pattern lengths
    melody_length = get_pattern_length_ticks(melody)
    catchy_melody_length = get_pattern_length_ticks(catchy_melody)
    
    # Repeat the catchy melody to match the main melody length
    if catchy_melody_length > 0:
        repeats_needed = max(1, melody_length // catchy_melody_length)
        catchy_melody_repeated = repeat_pattern(catchy_melody, repeats_needed, catchy_melody_length)
    else:
        catchy_melody_repeated = []
    
    # Create patterns dictionary for song structure
    patterns = {
        'melody': melody,
        'secondary_melody': secondary_melody,
        'catchy_melody': catchy_melody_repeated,
        'bg_melody': bg_melody_high,
        'bg_melody_low': bg_melody_low,
        'bass': bass_line,
        'funky_bass': funky_bass,
        'chords': chord_progression,
        'simple_drums': simple_drums,
        'complex_drums': complex_drums,
        # 'trap_fill': trap_fill
    }
    
    # Generate song structure
    sections = generate_song_structure(
        num_bars=num_bars,
        style=style,
        is_epic=is_epic,
        is_phonk=is_phonk,
        is_atmospheric=is_atmospheric,
        is_minimal=is_minimal,
        has_breakdown=has_breakdown
    )
    
    # Collect notes by channel
    notes_by_channel = {}
    
    # Process each section
    current_bar = 0
    for i, section in enumerate(sections):
        section_start_bar = current_bar
        section_length_ticks = section.num_bars * beats_per_bar * TICKS_PER_BEAT
        
        print(f"Adding section: {section.name} ({section.num_bars} bars)")
        
        # Process each instrument in the section
        for instrument_name, instrument_config in section.active_instruments.items():
            if instrument_name in patterns and instrument_config['pattern']:
                pattern = patterns[instrument_name]
                channel = instrument_config['channel']
                
                # Get pattern length
                pattern_length_ticks = get_pattern_length_ticks(pattern)
                if pattern_length_ticks == 0:
                    continue
                
                # Calculate how many times to repeat the pattern
                num_repeats = max(1, section_length_ticks // pattern_length_ticks)
                
                # Repeat the pattern
                repeated_pattern = repeat_pattern(pattern, num_repeats, pattern_length_ticks)
                
                # Offset the pattern to the current section
                offset_ticks = section_start_bar * beats_per_bar * TICKS_PER_BEAT
                
                # Add notes to the collection
                for note, velocity, time, duration in repeated_pattern:
                    # Only include notes that fall within this section
                    if time < section_length_ticks:
                        # Add the note with the offset
                        if channel not in notes_by_channel:
                            notes_by_channel[channel] = []
                        notes_by_channel[channel].append((note, velocity, time + offset_ticks, duration))
        
        # Move to the next section
        current_bar += section.num_bars
    
    # Create the MIDI file with the collected notes
    mid = create_midi_file_from_notes(output_file, notes_by_channel, tempo)
    
    # Add instrument programs to the track
    track = mid.tracks[0]
    
    # Set instrument programs
    set_instrument_program(track, SYNTH_VOICE, MELODY_CHANNEL)
    set_instrument_program(track, SYNTH_VOICE, 4)
    set_instrument_program(track, HARP, SECONDARY_BG_MELODY_CHANNEL)
    set_instrument_program(track, CHOIR, BG_MELODY_CHANNEL)
    set_instrument_program(track, ORGAN, CHORD_CHANNEL)
    set_instrument_program(track, HALO_PAD, SECONDARY_MELODY_CHANNEL)

    if is_atmospheric:
        # set_instrument_program(track, instruments["pad_warm"]["program"], MELODY_CHANNEL)
        set_instrument_program(track, instruments["pad_polysynth"]["program"], BG_MELODY_CHANNEL)
    else:
        set_instrument_program(track, instruments["lead_square"]["program"], MELODY_CHANNEL)
        set_instrument_program(track, instruments["lead_sawtooth"]["program"], SECONDARY_MELODY_CHANNEL)
        set_instrument_program(track, instruments["lead_voice"]["program"], SECONDARY_BG_MELODY_CHANNEL)
    
    if is_phonk:
        set_instrument_program(track, instruments["synth_bass_1"]["program"], BASS_CHANNEL)
        set_instrument_program(track, instruments["synth_bass_2"]["program"], SECONDARY_BASS_CHANNEL)
    else:
        set_instrument_program(track, instruments["finger_bass"]["program"], BASS_CHANNEL)
        set_instrument_program(track, instruments["slap_bass_1"]["program"], SECONDARY_BASS_CHANNEL)

    # Fix note timing to ensure playback   
    midi = fix_note_timings(mid)

    # Save the file again with the instrument programs
    midi.save(output_file)
    print(f"Full composition saved to {output_file} ({current_bar} bars)")
    
    return midi

def sort_and_fix_midi_track(track):
    """Sorts MIDI messages by time and fixes delta times."""
    events = []
    for msg in track:
        if not isinstance(msg, mido.MetaMessage) and hasattr(msg, 'time'):
            events.append(msg)
    
    # Sort events by time
    events.sort(key=lambda x: x.time)
    
    # Convert absolute time to delta time
    last_time = 0
    for msg in events:
        delta = msg.time - last_time
        last_time = msg.time
        msg.time = max(0, delta)  # Ensure non-negative delta time
    
    # Create a new track with properly timed messages
    new_track = mido.MidiTrack()
    
    # Add meta messages first
    for msg in track:
        if isinstance(msg, mido.MetaMessage):
            new_track.append(msg)
    
    # Add sorted note messages
    for msg in events:
        new_track.append(msg)
    
    return new_track

def main():
    """Main function to demonstrate the music generator."""
    # Example melody (note, velocity, time, duration)
    example_melody = [
    (60, 90, 0, 120),
    (67, 85, 120, 240),
    (65, 85, 360, 240),
    (67, 90, 600, 480),
    (65, 85, 1080, 240),
    (63, 80, 1320, 240),
    (62, 80, 1580, 360),

    (58, 90, 1920, 120),
    (65, 85, 2040, 240),
    (63, 85, 2280, 240),
    (65, 90, 2520, 480),
    (63, 85, 3000, 240),
    (62, 80, 3240, 240),
    (60, 80, 3480, 360),

    (60, 90, 3840, 120),
    (67, 85, 3960, 240),
    (65, 85, 4200, 240),
    (67, 90, 4440, 480),
    (65, 85, 4920, 240),
    (63, 80, 5160, 240),
    (62, 80, 5400, 360),

    (60, 90, 5760, 120),
    (67, 85, 5880, 240),
    (65, 85, 6120, 240),
    (67, 90, 6360, 480),
    (65, 85, 6840, 240),
    (63, 80, 7080, 240),
    (60, 80, 7320, 360),
    ]
    
    # Generate a standard composition
    generate_full_composition(
        melody=example_melody,
        root_note=60,  # C
        scale_type=MAJOR_SCALE,
        tempo=120,
        output_file="standard_composition.mid",
        style='trap',
        is_phonk=False,
        is_epic=False,
        is_atmospheric=False,
        is_minimal=False,
        has_breakdown=True,
        num_bars=44
    )
    
    # Generate a phonk composition
    generate_full_composition(
        melody=example_melody,
        root_note=60,  # C
        scale_type=MINOR_SCALE,  # Minor scale works better for phonk
        tempo=120,
        output_file="phonk_composition.mid",
        style='trap',
        is_phonk=True,
        is_epic=True,
        is_atmospheric=False,
        is_minimal=False,
        has_breakdown=True,
        num_bars=44
    )
    
    # Generate an atmospheric composition
    generate_full_composition(
        melody=example_melody,
        root_note=60,  # C
        scale_type=MAJOR_SCALE,
        tempo=100,  # Slower tempo for atmospheric feel
        output_file="atmospheric_composition.mid",
        style='ambient',
        is_phonk=False,
        is_epic=False,
        is_atmospheric=True,
        is_minimal=True,
        has_breakdown=True,
        num_bars=44
    )
    
    # Generate an epic composition
    generate_full_composition(
        melody=example_melody,
        root_note=60,  # C
        scale_type=MINOR_SCALE,  # Minor scale for epic feel
        tempo=140,  # Faster tempo for epic feel
        output_file="epic_composition.mid",
        style='trap',
        is_phonk=False,
        is_epic=True,
        is_atmospheric=False,
        is_minimal=False,
        has_breakdown=True,
        num_bars=44
    )

# main()