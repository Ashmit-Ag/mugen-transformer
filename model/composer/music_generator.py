"""
Main music generator module for the procedural music generation system.
Provides functions for generating complete musical compositions.
"""

import random
import json
import os
import mido
from .music_theory import get_scale_notes
from .melody_generator import create_melody, create_catchy_secondary_melody, create_bass_line, create_funky_bass_line, create_background_melody, create_secondary_melody
from .harmony_generator import generate_chord_progression
from .rhythm_generator import generate_drum_pattern
from .song_structure import generate_song_structure, apply_song_structure
from .midi_utils import create_midi_file, create_tracks_by_channel, add_program_change, fix_note_timings
from .audio_effects import apply_reverb, apply_delay, apply_filter

# Channel assignments
DRUM_CHANNEL = 9
BASS_CHANNEL = 0
CHORD_CHANNEL = 1
MELODY_CHANNEL = 2
BG_MELODY_CHANNEL = 3
SECONDARY_MELODY_CHANNEL = 4
SECONDARY_BG_MELODY_CHANNEL = 5
SECONDARY_BASS_CHANNEL = 6
SECONDARY_DRUM_CHANNEL = 10

def load_instruments():
    """
    Load instrument definitions from JSON file.
    
    Returns:
        dict: Dictionary of instrument definitions
    """
    try:
        with open('instruments.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default instruments if file not found or invalid
        return {
            "bass": {"program": 33, "channel": BASS_CHANNEL},
            "chords": {"program": 0, "channel": CHORD_CHANNEL},
            "melody": {"program": 80, "channel": MELODY_CHANNEL},
            "bg_melody": {"program": 73, "channel": BG_MELODY_CHANNEL},
            "secondary_melody": {"program": 81, "channel": SECONDARY_MELODY_CHANNEL},
            "secondary_bg_melody": {"program": 74, "channel": SECONDARY_BG_MELODY_CHANNEL},
            "secondary_bass": {"program": 35, "channel": SECONDARY_BASS_CHANNEL}
        }

def generate_music(
    output_file='output.mid',
    tempo=120,
    key=0,
    scale_type='major',
    num_bars=32,
    style='trap',
    complexity=0.5,
    is_epic=False,
    is_phonk=False,
    is_atmospheric=False,
    is_minimal=False,
    has_breakdown=True,
    instruments=None
):
    """
    Generate a complete musical composition.
    
    Args:
        output_file (str): Output MIDI filename
        tempo (int): Tempo in BPM
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        num_bars (int): Number of bars
        style (str): Music style
        complexity (float): Complexity of the music (0.0 to 1.0)
        is_epic (bool): Whether the music should have an epic feel
        is_phonk (bool): Whether the music should have a phonk feel
        is_atmospheric (bool): Whether the music should have an atmospheric feel
        is_minimal (bool): Whether the music should be minimal
        has_breakdown (bool): Whether the music should have a breakdown
        instruments (dict): Dictionary of instrument definitions
        
    Returns:
        str: Output filename
    """
    print(f"Generating {style} music in {key} {scale_type}...")
    
    # Load instruments if not provided
    if instruments is None:
        instruments = load_instruments()
    
    # Create a new MIDI file
    midi_file = create_midi_file(tempo=tempo)
    
    # Create tracks for each channel
    tracks_by_channel = create_tracks_by_channel(midi_file)
    
    # Set program changes for each instrument
    for instrument_name, instrument_data in instruments.items():
        if 'program' in instrument_data and 'channel' in instrument_data:
            program = instrument_data['program']
            channel = instrument_data['channel']
            
            # Skip drum channel (program changes don't apply to drums)
            if channel != DRUM_CHANNEL:
                add_program_change(tracks_by_channel[channel], program, channel)
    
    # Get scale notes
    scale = get_scale_notes(key, scale_type)
    
    # Set time signature
    beats_per_bar = 4  # 4/4 time
    
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
    
    # Generate patterns for each instrument
    patterns = {}
    
    # Generate chord progression
    chord_progression = generate_chord_progression(key, scale_type, 4, beats_per_bar)
    patterns['chords'] = [(notes, velocity, time, duration) for notes, velocity, time, duration in chord_progression]
     
    # Generate bass line
    bass_pattern = create_bass_line(
        key, scale_type, chord_progression, 4 ,beats_per_bar,
        complexity=complexity * 0.6, octave=2
    )
    patterns['bass'] = [(note, velocity, time, duration) for note, velocity, time, duration in bass_pattern]
    
    # Generate funky bass line
    funky_bass_pattern = create_funky_bass_line(
        key, scale_type, chord_progression, 4 ,beats_per_bar,
        complexity=complexity * 0.8, octave=2
    )
    patterns['funky_bass'] = [(note, velocity, time, duration) for note, velocity, time, duration in funky_bass_pattern]
    
    # Generate melody
    melody_pattern = create_melody(
        key, scale_type, 4, beats_per_bar,
        complexity=complexity, octave=4,
        rhythm_variation=0.6
    )
    # patterns['melody'] = [(note, velocity, time, duration) for note, velocity, time, duration in melody_pattern]
    
    # Generate secondary melody
    secondary_melody_pattern = create_secondary_melody(
        key, scale_type, 4, beats_per_bar,
        complexity=complexity * 0.9, octave=5,
    )
    # patterns['secondary_melody'] = [(note, velocity, time, duration) for note, velocity, time, duration in secondary_melody_pattern]
    
    # Generate background melody
    bg_melody_pattern = create_background_melody(
        key, scale_type, 4, beats_per_bar,
        complexity=complexity * 0.7, octave=4
    )
    patterns['bg_melody'] = [(note, velocity, time, duration) for note, velocity, time, duration in bg_melody_pattern]
    
    # Generate catchy melody
    catchy_melody_pattern = create_catchy_secondary_melody(
        key, scale_type, 4, beats_per_bar,
        complexity=complexity * 0.6, octave=4
    )
    patterns['catchy_melody'] = [(note, velocity, time, duration) for note, velocity, time, duration in catchy_melody_pattern]
    
    # Generate low background melody
    bg_melody_low_pattern = create_melody(
        key, scale_type, 4, beats_per_bar,
        complexity=complexity * 0.5, octave=3,
        rhythm_variation=0.3
    )
    patterns['bg_melody_low'] = [(note, velocity, time, duration) for note, velocity, time, duration in bg_melody_low_pattern]
    
    # Generate simple drum pattern
    simple_drum_pattern = generate_drum_pattern(
        4, beats_per_bar, complexity=complexity * 0.6, 
        is_phonk=is_phonk
    )
    patterns['simple_drums'] = [(note, velocity, time, duration) for note, velocity, time, duration in simple_drum_pattern]
    
    # Generate complex drum pattern
    complex_drum_pattern = generate_drum_pattern(
        4, beats_per_bar,
        complexity=complexity * 1.2, is_phonk=is_phonk
    )
    patterns['complex_drums'] = [(note, velocity, time, duration) for note, velocity, time, duration in complex_drum_pattern]
    
    # Generate trap fill pattern
    # trap_fill_pattern = generate_drum_pattern(
    #     1, beats_per_bar,
    #     complexity=1.0, is_fill=True
    # )
    # patterns['trap_fill'] = [(note, velocity, time, duration) for note, velocity, time, duration in trap_fill_pattern]
    
    # Apply song structure to the tracks
    total_bars = apply_song_structure(sections, patterns, tracks_by_channel, beats_per_bar, style, scale)
    
    # Fix note timings to ensure proper playback
    midi_file = fix_note_timings(midi_file)
    
    # Save the MIDI file
    midi_file.save(output_file)
    
    print(f"Generated {total_bars} bars of music. Saved to {output_file}")
    
    return output_file

# if __name__ == '__main__':
#     # Generate a trap beat
#     generate_music(
#         output_file='trap_beat.mid',
#         tempo=140,
#         key=0,  # C
#         scale_type=MINOR_SCALE,
#         num_bars=32,
#         style='trap',
#         complexity=0.7,
#         is_phonk=True
#     )
    
#     # Generate an ambient piece
#     generate_music(
#         output_file='ambient.mid',
#         tempo=90,
#         key=7,  # G
#         scale_type='major',
#         num_bars=32,
#         style='ambient',
#         complexity=0.5,
#         is_atmospheric=True
#     )