"""
Song structure module for the procedural music generation system.
Provides functions for creating and applying song structures.
"""

import random
from collections import namedtuple
from .midi_utils import add_note, add_chord, add_control_change
from .audio_effects import apply_filter_sweep
from .transitions import apply_transition, apply_ending_transition

# Define a Section namedtuple to represent a section of the song
Section = namedtuple('Section', ['name', 'intensity', 'num_bars', 'active_instruments'])

# Channel assignments (imported from music_generator.py)
DRUM_CHANNEL = 9
BASS_CHANNEL = 0
CHORD_CHANNEL = 1
MELODY_CHANNEL = 2
BG_MELODY_CHANNEL = 3
SECONDARY_MELODY_CHANNEL = 4
SECONDARY_BG_MELODY_CHANNEL = 5
SECONDARY_BASS_CHANNEL = 6
SECONDARY_DRUM_CHANNEL = 10

def generate_song_structure(num_bars=44, style='trap', is_epic=False, is_phonk=False, is_atmospheric=False, is_minimal=False, has_breakdown=True):
    """
    Generate a song structure with sections.
    
    Args:
        num_bars (int): Total number of bars in the song
        style (str): Music style
        is_epic (bool): Whether the song should have an epic feel
        is_phonk (bool): Whether the song should have a phonk feel
        is_atmospheric (bool): Whether the song should have an atmospheric feel
        is_minimal (bool): Whether the song should be minimal
        has_breakdown (bool): Whether the song should have a breakdown
        
    Returns:
        list: List of Section objects
    """
    # Ensure num_bars is divisible by 4
    num_bars = (num_bars // 4) * 4
    
    # Number of sections (each section is 4 bars)
    num_sections = num_bars // 4
    
    # Define section types with their typical intensity levels
    section_types = {
        'intro': 0.3,
        'verse': 0.5,
        'pre_chorus': 0.7,
        'chorus': 0.9,
        'breakdown': 0.2,
        'bridge': 0.6,
        'build_up': 0.8,
        'drop': 1.0,
        'outro': 0.4
    }
    
    # Adjust intensities based on style
    if is_epic:
        for section in ['chorus', 'drop', 'build_up']:
            section_types[section] = min(1.0, section_types[section] * 1.2)
    
    if is_atmospheric:
        for section in section_types:
            section_types[section] = max(0.1, section_types[section] * 0.8)
    
    if is_minimal:
        for section in section_types:
            section_types[section] = max(0.1, section_types[section] * 0.7)
    
    # Create a list to hold the sections
    sections = []
    
    # Define a standard song structure pattern
    # Each element represents a 4-bar section
    structure_pattern = []
    
    # Create a more complex structure based on the number of sections
    if num_sections <= 6:
        # Simple structure for short songs
        structure_pattern = ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro'][:num_sections]
    elif num_sections <= 10:
        # Medium structure
        structure_pattern = ['intro', 'verse', 'pre_chorus', 'chorus', 'verse', 'pre_chorus', 'chorus', 'bridge', 'chorus', 'outro'][:num_sections]
    else:
        # Complex structure for longer songs
        base_pattern = ['intro', 'verse', 'pre_chorus', 'chorus', 'verse', 'pre_chorus', 'chorus']
        
        # Add breakdown and build-up if requested
        if has_breakdown:
            base_pattern.extend(['breakdown', 'build_up'])
        
        # Add drop for trap and phonk styles
        if style == 'trap' or is_phonk:
            base_pattern.append('drop')
        
        # Add bridge and final chorus
        base_pattern.extend(['bridge', 'chorus'])
        
        # Add outro
        base_pattern.append('outro')
        
        # If we still need more sections, add variations
        while len(base_pattern) < num_sections:
            # Add additional verse-chorus pairs
            insert_pos = random.randint(4, len(base_pattern) - 2)
            base_pattern.insert(insert_pos, 'verse')
            base_pattern.insert(insert_pos + 1, 'chorus')
        
        # Trim if necessary
        structure_pattern = base_pattern[:num_sections]
    
    # Ensure we have exactly the right number of sections
    while len(structure_pattern) < num_sections:
        structure_pattern.append(random.choice(['verse', 'chorus', 'bridge']))
    
    # Create the sections
    for i, section_name in enumerate(structure_pattern):
        # Get the base intensity for this section type
        intensity = section_types[section_name]
        
        # Add slight variation to intensity
        intensity += random.uniform(-0.1, 0.1)
        intensity = max(0.1, min(1.0, intensity))
        
        # Determine active instruments based on section type and intensity
        active_instruments = {}
        
        # Common configuration for all sections
        active_instruments['simple_drums'] = {
            'pattern': section_name != 'breakdown' and (section_name == 'intro' or intensity < 0.7),
            'channel': DRUM_CHANNEL
        }
        
        active_instruments['complex_drums'] = {
            'pattern': section_name != 'breakdown' and intensity >= 0.7,
            'channel': DRUM_CHANNEL
        }
        
        active_instruments['bass'] = {
            'pattern': section_name != 'breakdown' and intensity >= 0.3,
            'channel': BASS_CHANNEL
        }
        
        active_instruments['funky_bass'] = {
            'pattern': section_name != 'breakdown' and intensity >= 0.8,
            'channel': SECONDARY_BASS_CHANNEL
        }
        
        active_instruments['chords'] = {
            'pattern': True,  # Chords are always active
            'channel': CHORD_CHANNEL
        }
        
        active_instruments['melody'] = {
            'pattern': section_name not in ['intro', 'breakdown', 'outro'] and intensity >= 0.5,
            'channel': MELODY_CHANNEL
        }
        
        active_instruments['secondary_melody'] = {
            'pattern': section_name == 'intro' or intensity >= 0.7,
            'channel': SECONDARY_MELODY_CHANNEL
        }
        
        active_instruments['catchy_melody'] = {
            'pattern': section_name in ['chorus', 'drop'] and intensity >= 0.8,
            'channel': BG_MELODY_CHANNEL
        }
        
        active_instruments['bg_melody'] = {
            'pattern': section_name not in ['intro', 'breakdown'] and intensity >= 0.6,
            'channel': BG_MELODY_CHANNEL
        }
        
        active_instruments['bg_melody_low'] = {
            'pattern': section_name in ['bridge', 'build_up'] and intensity >= 0.7,
            'channel': SECONDARY_BG_MELODY_CHANNEL
        }
        
        active_instruments['trap_fill'] = {
            'pattern': False,  # Used only for transitions
            'channel': SECONDARY_DRUM_CHANNEL
        }
        
        # Special configurations for specific sections
        if section_name == 'intro':

            choice =  random.choice([True, False])
            # In intro, activate chords, secondary melody, and secondary bass
            active_instruments['chords']['pattern'] = True 
            active_instruments['secondary_melody']['pattern'] = False 
            active_instruments['bass']['pattern'] = choice
            active_instruments['funky_bass']['pattern'] = False
            active_instruments['simple_drums']['pattern'] = False  # Sometimes have drums in intro
            active_instruments['complex_drums']['pattern'] = False
            active_instruments['melody']['pattern'] = False
            active_instruments['catchy_melody']['pattern'] = False 
            active_instruments['bg_melody']['pattern'] = False
            active_instruments['bg_melody_low']['pattern'] = False
        
        elif section_name == 'breakdown':
            # In breakdown, minimal instrumentation
            active_instruments['chords']['pattern'] = True
            active_instruments['secondary_melody']['pattern'] = random.choice([True, False])
            active_instruments['bass']['pattern'] = False
            active_instruments['funky_bass']['pattern'] = False
            active_instruments['simple_drums']['pattern'] = False
            active_instruments['complex_drums']['pattern'] = False
            active_instruments['melody']['pattern'] = False
            active_instruments['catchy_melody']['pattern'] = False
            active_instruments['bg_melody']['pattern'] = False
            active_instruments['bg_melody_low']['pattern'] = False
        
        elif section_name == 'build_up':
            # In build-up, gradually introduce instruments
            active_instruments['chords']['pattern'] = True
            active_instruments['secondary_melody']['pattern'] = True
            active_instruments['bass']['pattern'] = True
            active_instruments['funky_bass']['pattern'] = False
            active_instruments['simple_drums']['pattern'] = True
            active_instruments['complex_drums']['pattern'] = False
            active_instruments['melody']['pattern'] = True
            active_instruments['catchy_melody']['pattern'] = False
            active_instruments['bg_melody']['pattern'] = True
            active_instruments['bg_melody_low']['pattern'] = True
        
        elif section_name == 'drop':
            # In drop, all instruments active
            active_instruments['chords']['pattern'] = True
            active_instruments['secondary_melody']['pattern'] = True
            active_instruments['bass']['pattern'] = False
            active_instruments['funky_bass']['pattern'] = True
            active_instruments['simple_drums']['pattern'] = False
            active_instruments['complex_drums']['pattern'] = True
            active_instruments['melody']['pattern'] = True
            active_instruments['catchy_melody']['pattern'] = True
            active_instruments['bg_melody']['pattern'] = True
            active_instruments['bg_melody_low']['pattern'] = False
        
        # Create the section
        section = Section(
            name=section_name,
            intensity=intensity,
            num_bars=4,  # All sections are 4 bars
            active_instruments=active_instruments
        )
        
        sections.append(section)
    
    return sections

def apply_song_structure(sections, patterns, tracks_by_channel, beats_per_bar, style, scale):
    """
    Apply a song structure to multiple MIDI tracks.
    
    Args:
        sections (list): List of Section objects
        patterns (dict): Dictionary of patterns (melody, bass, etc.)
        tracks_by_channel (dict): Dictionary of MIDI tracks by channel
        beats_per_bar (int): Number of beats per bar
        style (str): Music style
        scale (list): List of scale notes
        
    Returns:
        int: Total number of bars
    """
    current_bar = 0
    ticks_per_bar = beats_per_bar * 480  # Assuming 480 ticks per beat
    
    # Process each section
    for i, section in enumerate(sections):
        section_start_tick = current_bar * ticks_per_bar
        
        print(f"Processing section: {section.name} (bars {current_bar+1}-{current_bar+section.num_bars})")
        
        # Apply transition if not the first section
        if i > 0:
            prev_section = sections[i-1]
            intensity_change = section.intensity - prev_section.intensity
            
            # Apply transition based on intensity change
            for channel, track in tracks_by_channel.items():
                apply_transition(track, prev_section.intensity, section.intensity, 
                                section_start_tick, ticks_per_bar, style, scale)
        
        # Process each active instrument in the section
        for instrument_name, instrument_config in section.active_instruments.items():
            if instrument_name in patterns and instrument_config['pattern']:
                pattern = patterns[instrument_name]
                channel = instrument_config['channel']
                
                # Get the track for this channel
                track = tracks_by_channel[channel]
                
                # Get pattern length
                pattern_length = 0
                for _, _, time, duration in pattern:
                    pattern_length = max(pattern_length, time + duration)
                
                if pattern_length == 0:
                    continue
                
                # Calculate how many times to repeat the pattern
                section_length_ticks = section.num_bars * ticks_per_bar
                repeats = max(1, section_length_ticks // pattern_length)
                
                # Add the pattern to the track
                for repeat in range(repeats):
                    for note, velocity, time, duration in pattern:
                        # Only include notes that fall within this section
                        if time + (repeat * pattern_length) < section_length_ticks:
                            # Skip rest notes (represented by note=-1)
                            if note >= 0:
                                # Add the note with the offset
                                add_note(track, note, velocity, 
                                        section_start_tick + time + (repeat * pattern_length), 
                                        duration, channel)
        
        # Apply special effects based on section type
        if section.name == 'build_up':
            # Apply filter sweep for build-up
            melody_track = tracks_by_channel[MELODY_CHANNEL]
            apply_filter_sweep(melody_track, 20, 127, 100, section.num_bars * ticks_per_bar, 
                              section_start_tick, MELODY_CHANNEL)
        
        elif section.name == 'drop':
            # Apply filter sweep for drop
            melody_track = tracks_by_channel[MELODY_CHANNEL]
            apply_filter_sweep(melody_track, 127, 20, 80, ticks_per_bar, 
                              section_start_tick, MELODY_CHANNEL)
        
        # Move to the next section
        current_bar += section.num_bars
    
    # Apply ending transition to all relevant tracks
    for channel, track in tracks_by_channel.items():
        if channel in [MELODY_CHANNEL, BASS_CHANNEL, CHORD_CHANNEL, DRUM_CHANNEL]:
            apply_ending_transition(track, sections[-1].intensity, 
                                  current_bar * ticks_per_bar, ticks_per_bar, style, scale)
    
    return current_bar