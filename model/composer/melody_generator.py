"""
Melody generator module for the procedural music generation system.
Provides functions for creating melodies and melodic patterns.
"""

import random
from .music_theory import get_scale_notes, get_chord_notes
from .midi_utils import TICKS_PER_BEAT

# Global velocity settings for all melodies
MELODY_VELOCITY_MIN = 100
MELODY_VELOCITY_MAX = 120
SECONDARY_MELODY_VELOCITY_MIN = 90
SECONDARY_MELODY_VELOCITY_MAX = 110
BG_MELODY_VELOCITY_MIN = 80
BG_MELODY_VELOCITY_MAX = 100

def create_melody(key, scale_type, num_bars, beats_per_bar, complexity=0.5, octave=4, rhythm_variation=0.5):
    """
    Create a melody.
    
    Args:
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the melody (0.0 to 1.0)
        octave (int): Base octave for the melody
        rhythm_variation (float): Variation in rhythm (0.0 to 1.0)
        
    Returns:
        list: Melody as (note, velocity, time, duration) tuples
    """
    melody = []
    
    # Get scale notes
    scale = get_scale_notes(key, scale_type)
    
    # Transpose scale to the specified octave
    scale_notes = [note for note in scale]
    
    # Add notes from adjacent octaves for more variety
    lower_octave = [note - 6 for note in scale_notes]
    higher_octave = [note + 6 for note in scale_notes]
    
    # Combine all available notes
    available_notes = lower_octave + scale_notes + higher_octave
    
    # Filter out notes outside the MIDI range
    available_notes = [note for note in available_notes if 0 <= note <= 127]
    
    # Calculate ticks per bar
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    
    # Determine note durations based on complexity
    if complexity < 0.3:
        # Simple rhythm - quarter and half notes
        possible_durations = [TICKS_PER_BEAT, TICKS_PER_BEAT * 2]
        duration_weights = [0.7, 0.3]
    elif complexity < 0.7:
        # Moderate rhythm - eighth, quarter, and half notes
        possible_durations = [TICKS_PER_BEAT // 2, TICKS_PER_BEAT, TICKS_PER_BEAT * 2]
        duration_weights = [0.3, 0.5, 0.2]
    else:
        # Complex rhythm - sixteenth, eighth, quarter, and dotted notes
        possible_durations = [TICKS_PER_BEAT // 4, TICKS_PER_BEAT // 2, TICKS_PER_BEAT, 
                             TICKS_PER_BEAT * 3 // 2]
        duration_weights = [0.2, 0.4, 0.3, 0.1]
    
    # Generate the melody
    current_time = 0
    total_ticks = num_bars * ticks_per_bar
    
    while current_time < total_ticks:
        # Determine if this is a rest
        is_rest = random.random() < 0.2 * rhythm_variation
        
        if is_rest:
            # Choose a duration for the rest
            duration = random.choices(possible_durations, weights=duration_weights)[0]
            
            # Add the rest (represented as a tuple with note=-1)
            melody.append((-1, 0, current_time, duration))
        else:
            # Choose a note from the available notes
            note = random.choice(available_notes)
            
            # Choose a duration
            duration = random.choices(possible_durations, weights=duration_weights)[0]
            
            # Apply some rhythm variation
            if random.random() < rhythm_variation:
                duration = int(duration * random.choice([0.5, 0.75, 1.0, 1.5]))
            
            # Ensure the duration is at least a 16th note
            duration = max(TICKS_PER_BEAT // 4, duration)
            
            # Determine velocity based on beat position
            beat_position = (current_time % ticks_per_bar) / TICKS_PER_BEAT
            
            if beat_position < 0.1:
                # Emphasize downbeats
                velocity = random.randint(MELODY_VELOCITY_MIN + 10, MELODY_VELOCITY_MAX)
            else:
                velocity = random.randint(MELODY_VELOCITY_MIN, MELODY_VELOCITY_MAX - 10)
            
            # Add the note
            melody.append((note, velocity, current_time, duration))
        
        # Move to the next note
        current_time += duration
    
    # Trim the melody to fit exactly within the specified number of bars
    trimmed_melody = []
    for note, velocity, time, duration in melody:
        if time + duration <= total_ticks:
            trimmed_melody.append((note, velocity, time, duration))
        else:
            # Trim the last note
            trimmed_duration = total_ticks - time
            if trimmed_duration > 0:
                trimmed_melody.append((note, velocity, time, trimmed_duration))
    
    return trimmed_melody

def create_secondary_melody(key, scale_type, num_bars, beats_per_bar, complexity=0.4, octave=5):
    """
    Create a secondary melody with less complexity.
    
    Args:
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the melody (0.0 to 1.0)
        octave (int): Base octave for the melody
        
    Returns:
        list: Melody as (note, velocity, time, duration) tuples
    """
    # Create a melody with reduced complexity and rhythm variation
    return create_melody(key, scale_type, num_bars, beats_per_bar, 
                        complexity=min(0.5, complexity), 
                        octave=octave, 
                        rhythm_variation=0.3)

def create_background_melody(key, scale_type, num_bars, beats_per_bar, complexity=0.3, octave=3):
    """
    Create a background melody with less complexity and lower octave.
    
    Args:
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the melody (0.0 to 1.0)
        octave (int): Base octave for the melody
        
    Returns:
        list: Melody as (note, velocity, time, duration) tuples
    """
    bg_melody = []
    
    # Get scale notes
    scale = get_scale_notes(key, scale_type)
    
    # Transpose scale to the specified octave
    scale_notes = [note + 6 for note in scale]
    
    # Filter out notes outside the MIDI range
    scale_notes = [note for note in scale_notes if 0 <= note <= 127]
    
    # Calculate ticks per bar
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    
    # Determine note durations based on complexity
    if complexity < 0.3:
        # Simple rhythm - half and whole notes
        possible_durations = [TICKS_PER_BEAT * 2, TICKS_PER_BEAT * 4]
        duration_weights = [0.7, 0.3]
    else:
        # Moderate rhythm - quarter and half notes
        possible_durations = [TICKS_PER_BEAT, TICKS_PER_BEAT * 2]
        duration_weights = [0.4, 0.6]
    
    # Generate the melody
    current_time = 0
    total_ticks = num_bars * ticks_per_bar
    
    while current_time < total_ticks:
        # Determine if this is a rest
        is_rest = random.random() < 0.3
        
        if is_rest:
            # Choose a duration for the rest
            duration = random.choices(possible_durations, weights=duration_weights)[0]
            
            # Add the rest (represented as a tuple with note=-1)
            bg_melody.append((-1, 0, current_time, duration))
        else:
            # Choose a note from the scale
            note = random.choice(scale_notes)
            
            # Choose a duration
            duration = random.choices(possible_durations, weights=duration_weights)[0]
            
            # Determine velocity (lower for background melody)
            velocity = random.randint(BG_MELODY_VELOCITY_MIN, BG_MELODY_VELOCITY_MAX)
            
            # Add the note
            bg_melody.append((note, velocity, current_time, duration))
        
        # Move to the next note
        current_time += duration
    
    # Trim the melody to fit exactly within the specified number of bars
    trimmed_melody = []
    for note, velocity, time, duration in bg_melody:
        if time + duration <= total_ticks:
            trimmed_melody.append((note, velocity, time, duration))
        else:
            # Trim the last note
            trimmed_duration = total_ticks - time
            if trimmed_duration > 0:
                trimmed_melody.append((note, velocity, time, trimmed_duration))
    
    return trimmed_melody

def create_catchy_secondary_melody(key, scale_type, num_bars, beats_per_bar, complexity=0.6, octave=4):
    """
    Create a catchy secondary melody with more rhythmic interest.
    
    Args:
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the melody (0.0 to 1.0)
        octave (int): Base octave for the melody
        
    Returns:
        list: Melody as (note, velocity, time, duration) tuples
    """
    catchy_melody = []
    
    # Get scale notes
    scale = get_scale_notes(key, scale_type)
    
    # Transpose scale to the specified octave
    scale_notes = [note for note in scale] 
    higher_octave = [note + 12 for note in scale_notes]
    
    # Combine all available notes
    available_notes = scale_notes + higher_octave
    
    # Filter out notes outside the MIDI range
    available_notes = [note for note in available_notes if 0 <= note <= 127]
    
    # Calculate ticks per bar
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    
    # Create a rhythmic pattern for the catchy melody
    pattern_length = beats_per_bar * 2  # 2 bars pattern
    pattern = []
    
    # Generate a rhythmic pattern based on complexity
    if complexity < 0.4:
        # Simple pattern - quarter notes with occasional eighth notes
        for i in range(pattern_length):
            if i % 2 == 0 or random.random() < 0.3:
                pattern.append(1)  # Note
            else:
                pattern.append(0)  # Rest
    elif complexity < 0.7:
        # Moderate pattern - eighth notes with occasional sixteenth notes
        for i in range(pattern_length * 2):
            if i % 3 == 0 or random.random() < 0.4:
                pattern.append(1)  # Note
            else:
                pattern.append(0)  # Rest
    else:
        # Complex pattern - varied rhythm
        for i in range(pattern_length * 2):
            if i % 4 == 0 or i % 7 == 0 or random.random() < 0.3:
                pattern.append(1)  # Note
            else:
                pattern.append(0)  # Rest
    
    # Generate the melody using the pattern
    total_ticks = num_bars * ticks_per_bar
    pattern_ticks = pattern_length * TICKS_PER_BEAT
    
    for bar in range(num_bars):
        bar_start = bar * ticks_per_bar
        
        # Apply the pattern for this bar
        for i, has_note in enumerate(pattern):
            if has_note:
                # Calculate position within the pattern
                position = i % len(pattern)
                time = bar_start + (position * TICKS_PER_BEAT // 2)
                
                # Skip if we've exceeded the total duration
                if time >= total_ticks:
                    continue
                
                # Choose a note from the available notes
                # Use more consonant notes on strong beats
                if position % 4 == 0:
                    # Strong beat - use root, third, or fifth
                    note_indices = [0, 2, 4]  # Root, third, fifth
                    note_index = random.choice(note_indices)
                    note = scale_notes[note_index % len(scale_notes)]
                else:
                    # Weak beat - use any scale note
                    note = random.choice(available_notes)
                
                # Determine duration based on position
                if position % 4 == 0:
                    # Longer notes on strong beats
                    duration = TICKS_PER_BEAT // (1 if random.random() < 0.7 else 2)
                else:
                    # Shorter notes on weak beats
                    duration = TICKS_PER_BEAT // (2 if random.random() < 0.7 else 4)
                
                # Ensure we don't exceed the total duration
                if time + duration > total_ticks:
                    duration = total_ticks - time
                
                # Skip if duration is too short
                if duration <= 0:
                    continue
                
                # Determine velocity based on position
                if position % 4 == 0:
                    # Emphasize strong beats
                    velocity = random.randint(SECONDARY_MELODY_VELOCITY_MIN + 10, SECONDARY_MELODY_VELOCITY_MAX)
                else:
                    velocity = random.randint(SECONDARY_MELODY_VELOCITY_MIN, SECONDARY_MELODY_VELOCITY_MAX - 10)
                
                # Add the note
                catchy_melody.append((note, velocity, time, duration))
    
    return catchy_melody

def create_bass_line(key, scale_type, chord_progression, num_bars, beats_per_bar, complexity=0.5, octave=2):
    """
    Create a bass line based on a chord progression.
    
    Args:
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        chord_progression (list): Chord progression as (chord_notes, velocity, time, duration) tuples
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the bass line (0.0 to 1.0)
        octave (int): Base octave for the bass line
        
    Returns:
        list: Bass line as (note, velocity, time, duration) tuples
    """
    bass_line = []
    
    # Get scale notes
    scale = get_scale_notes(key, scale_type)
    
    # Transpose scale to the specified octave
    scale_notes = [note + (octave * 2) for note in scale]
    
    # Filter out notes outside the MIDI range
    scale_notes = [note for note in scale_notes if 0 <= note <= 127]
    
    # Calculate ticks per bar
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    
    # Generate the bass line based on the chord progression
    for chord_notes, _, chord_time, chord_duration in chord_progression:
        # Get the root note of the chord (lowest note)
        root_note = chord_notes
        
        # Transpose to the bass octave
        while root_note >= 60:  # Middle C
            root_note -= 12
        
        # Ensure the note is within MIDI range
        if root_note < 0:
            root_note += 12
        
        # Determine the pattern based on complexity
        if complexity < 0.3:
            # Simple pattern - root note on each beat
            for beat in range(beats_per_bar):
                time = chord_time + (beat * TICKS_PER_BEAT)
                
                # Skip if we've moved past this chord
                if time >= chord_time + chord_duration:
                    continue
                
                # Determine duration
                duration = min(TICKS_PER_BEAT, chord_time + chord_duration - time)
                
                # Determine velocity
                if beat == 0:
                    # Emphasize downbeat
                    velocity = random.randint(90, 110)
                else:
                    velocity = random.randint(70, 90)
                
                # Add the note
                bass_line.append((root_note, velocity, time, duration))
        
        elif complexity < 0.7:
            # Moderate pattern - root note with occasional fifth
            for beat in range(beats_per_bar):
                time = chord_time + (beat * TICKS_PER_BEAT)
                
                # Skip if we've moved past this chord
                if time >= chord_time + chord_duration:
                    continue
                
                # Determine note
                if beat == 0 or random.random() < 0.7:
                    # Root note
                    note = root_note
                else:
                    # Fifth
                    fifth = (root_note + 7) % 12 + (root_note // 12) * 12
                    if fifth > root_note + 7:
                        fifth -= 12
                    note = fifth
                
                # Determine duration
                duration = min(TICKS_PER_BEAT, chord_time + chord_duration - time)
                
                # Determine velocity
                if beat == 0:
                    # Emphasize downbeat
                    velocity = random.randint(90, 110)
                else:
                    velocity = random.randint(70, 90)
                
                # Add the note
                bass_line.append((note, velocity, time, duration))
        
        else:
            # Complex pattern - walking bass
            for beat in range(beats_per_bar * 2):  # Eighth notes
                time = chord_time + (beat * TICKS_PER_BEAT // 2)
                
                # Skip if we've moved past this chord
                if time >= chord_time + chord_duration:
                    continue
                
                # Determine note
                if beat % 2 == 0:
                    # On the beat - root note
                    note = root_note
                else:
                    # Off the beat - passing tone or chord tone
                    if random.random() < 0.7:
                        # Chord tone (third or fifth)
                        interval = random.choice([3, 4, 7])
                        passing_note = (root_note + interval) % 12 + (root_note // 12) * 12
                        if passing_note > root_note + 7:
                            passing_note -= 12
                        note = passing_note
                    else:
                        # Passing tone from scale
                        scale_index = random.randint(0, len(scale_notes) - 1)
                        note = scale_notes[scale_index]
                
                # Determine duration
                duration = min(TICKS_PER_BEAT // 2, chord_time + chord_duration - time)
                
                # Determine velocity
                if beat % 2 == 0:
                    # Emphasize on-beat notes
                    velocity = random.randint(80, 100)
                else:
                    velocity = random.randint(70, 90)
                
                # Add the note
                bass_line.append((note, velocity, time, duration))
    
    return bass_line

def create_funky_bass_line(key, scale_type, chord_progression, num_bars, beats_per_bar, complexity=0.7, octave=2):
    """
    Create a funky bass line with more rhythmic variation and syncopation.
    
    Args:
        key (int): Key (0=C, 1=C#, etc.)
        scale_type (str): Scale type ('major', 'minor', etc.)
        chord_progression (list): Chord progression as (chord_notes, velocity, time, duration) tuples
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the bass line (0.0 to 1.0)
        octave (int): Base octave for the bass line
        
    Returns:
        list: Bass line as (note, velocity, time, duration) tuples
    """
    funky_bass = []
    
    # Get scale notes
    scale = get_scale_notes(key, scale_type)
    
    # Transpose scale to the specified octave
    scale_notes = [note + (octave * 12) for note in scale]
    
    # Filter out notes outside the MIDI range
    scale_notes = [note for note in scale_notes if 0 <= note <= 127]
    
    # Calculate ticks per bar
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    
    # Define some funky rhythmic patterns (16th note grid)
    funky_patterns = [
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],  # Pattern 1
        [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],  # Pattern 2
        [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0],  # Pattern 3
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],  # Pattern 4
    ]
    
    # Choose a pattern based on complexity
    if complexity < 0.5:
        pattern = funky_patterns[0]
    elif complexity < 0.7:
        pattern = random.choice(funky_patterns[:2])
    else:
        pattern = random.choice(funky_patterns)
    
    # Generate the bass line based on the chord progression
    for chord_notes, _, chord_time, chord_duration in chord_progression:
        # Get the root note of the chord (lowest note)
        root_note = chord_notes
        
        # Transpose to the bass octave
        while root_note >= 60:  # Middle C
            root_note -= 12
        
        # Ensure the note is within MIDI range
        if root_note < 0:
            root_note += 12
        
        # Calculate number of 16th notes in this chord
        sixteenth_notes = chord_duration // (TICKS_PER_BEAT // 4)
        
        # Apply the pattern to this chord
        for i in range(sixteenth_notes):
            pattern_index = i % len(pattern)
            
            if pattern[pattern_index]:
                time = chord_time + (i * TICKS_PER_BEAT // 4)
                
                # Determine note
                if i == 0 or random.random() < 0.6:
                    # Root note
                    note = root_note
                elif random.random() < 0.7:
                    # Chord tone (third or fifth)
                    interval = random.choice([3, 4, 7])
                    chord_tone = (root_note + interval) % 12 + (root_note // 12) * 12
                    if chord_tone > root_note + 7:
                        chord_tone -= 12
                    note = chord_tone
                else:
                    # Scale tone
                    note = random.choice(scale_notes)
                
                # Determine duration (mostly 16th notes, but occasional 8th notes)
                if random.random() < 0.2:
                    duration = TICKS_PER_BEAT // 2  # 8th note
                else:
                    duration = TICKS_PER_BEAT // 4  # 16th note
                
                # Ensure we don't exceed the chord duration
                duration = min(duration, chord_time + chord_duration - time)
                
                # Skip if duration is invalid
                if duration <= 0:
                    continue
                
                # Determine velocity with some variation for groove
                if i % 4 == 0:
                    # Emphasize downbeats
                    velocity = random.randint(90, 110)
                elif pattern_index in [4, 12]:  # Emphasize certain syncopated beats
                    velocity = random.randint(85, 105)
                else:
                    velocity = random.randint(75, 95)
                
                # Add the note
                funky_bass.append((note, velocity, time, duration))
    
    return funky_bass