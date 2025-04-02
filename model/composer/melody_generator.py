"""
Melody generator module for the procedural music generation system.
Provides functions for creating various types of melodies.
"""

import random
from .music_theory import get_scale_notes, get_chord_from_scale

def create_background_melody(main_melody, scale):
    """
    Create a background melody that complements the main melody.
    
    Args:
        main_melody (list): List of (note, velocity, time, duration) tuples
        scale (list): List of scale notes
        
    Returns:
        list: Background melody as (note, velocity, time, duration) tuples
    """
    if not main_melody:
        return []
    
    bg_melody = []
    
    # Extract rhythm pattern from main melody
    rhythm_pattern = [(time, duration) for _, _, time, duration in main_melody]
    
    # Use a different starting point in the scale
    scale_offset = 2  # Start from the third note of the scale
    
    # Create a more coherent background melody
    for i, (_, _, time, duration) in enumerate(main_melody):
        # Only add a note for every other note in the main melody to create space
        if i % 2 == 0:
            # Choose a note from the scale that complements the main melody
            # Use a more predictable pattern based on position in the scale
            scale_position = (i // 2 + scale_offset) % len(scale)
            note = scale[scale_position]
            
            # Adjust velocity to be softer than the main melody
            velocity = 60
            
            # Add the note to the background melody
            bg_melody.append((note, velocity, time, duration))
    
    return bg_melody

def create_catchy_secondary_melody(scale, root_note):
    """
    Create a catchy secondary melody (hook) based on the scale.
    
    Args:
        scale (list): List of scale notes
        root_note (int): Root note of the scale
        
    Returns:
        list: Catchy melody as (note, velocity, time, duration) tuples
    """
    # Create a short, memorable pattern
    catchy_melody = []
    
    # Define a rhythmic pattern (in 16th notes)
    # 1 = note, 0 = rest
    rhythm_pattern = [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1]
    
    # Define a melodic pattern (scale degrees)
    # This creates a more musical and less random pattern
    melodic_pattern = [0, 2, 4, 2, 0, 4, 2, 5]
    
    # Duration of a 16th note in ticks (assuming 480 ticks per beat)
    sixteenth_note = 120
    
    # Create the melody
    current_time = 0
    for i, rhythm_value in enumerate(rhythm_pattern):
        if rhythm_value == 1:
            # Get the note from the melodic pattern
            scale_position = melodic_pattern[i % len(melodic_pattern)]
            note = scale[scale_position % len(scale)]
            
            # Adjust to the appropriate octave
            while note < root_note:
                note += 12
            
            # Add some velocity variation for expressiveness
            velocity = random.randint(70, 90)
            
            # Duration is one 16th note
            duration = sixteenth_note
            
            # Add the note to the melody
            catchy_melody.append((note, velocity, current_time, duration))
        
        # Move to the next 16th note position
        current_time += sixteenth_note
    
    return catchy_melody

def create_melodic_fill(scale, duration_ticks, intensity=0.5):
    """
    Create a melodic fill for transitions.
    
    Args:
        scale (list): List of scale notes
        duration_ticks (int): Duration of the fill in ticks
        intensity (float): Intensity of the fill (0.0 to 1.0)
        
    Returns:
        list: Melodic fill as (note, velocity, time, duration) tuples
    """
    fill = []
    
    # Number of notes in the fill based on intensity
    num_notes = int(4 + intensity * 8)
    
    # Duration of each note
    note_duration = duration_ticks // num_notes
    
    # Create an ascending or descending run
    ascending = random.choice([True, False])
    
    # Starting position in the scale
    start_pos = random.randint(0, len(scale) - 1)
    
    for i in range(num_notes):
        # Calculate position in the scale
        if ascending:
            pos = (start_pos + i) % len(scale)
        else:
            pos = (start_pos - i) % len(scale)
        
        # Get the note
        note = scale[pos]
        
        # Adjust to appropriate octave
        octave_adjust = (i // len(scale)) * 12 if ascending else -(i // len(scale)) * 12
        note += octave_adjust
        
        # Calculate time
        time = i * note_duration
        
        # Calculate velocity (crescendo or decrescendo)
        if ascending:
            velocity = 70 + int(i * 20 / num_notes)
        else:
            velocity = 90 - int(i * 20 / num_notes)
        
        # Add the note
        fill.append((note, velocity, time, note_duration))
    
    return fill