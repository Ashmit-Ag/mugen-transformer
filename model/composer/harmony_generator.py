import random
from .music_theory import get_scale_notes, get_chord_notes
from .music_theory import MAJOR_SCALE, MINOR_SCALE, MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD
from .midi_utils import TICKS_PER_BEAT

def generate_bass_line(root_note, scale_type, num_bars, beats_per_bar, complexity=0.5, is_funky=False):
    """Generate a bass line based on the root note and scale."""
    scale = get_scale_notes(root_note, scale_type)
    bass_line = []
    
    # Adjust complexity for funky bass
    if is_funky:
        complexity = min(complexity * 1.5, 1.0)
        
    # Determine rhythm pattern based on complexity
    if complexity < 0.3:
        # Simple: Quarter notes
        notes_per_beat = 1
    elif complexity < 0.6:
        # Medium: Eighth notes
        notes_per_beat = 2
    else:
        # Complex: Sixteenth notes or triplets
        notes_per_beat = 4 if random.random() > 0.5 else 3
    
    ticks_per_note = TICKS_PER_BEAT // notes_per_beat
    
    for bar in range(num_bars):
        for beat in range(beats_per_bar):
            for note_idx in range(notes_per_beat):
                # Determine if we play a note or rest
                if random.random() < (0.7 + (0.3 * complexity)):
                    # Choose a note from the scale, with emphasis on root and fifth
                    if random.random() < 0.6 and not is_funky:
                        # Root or fifth
                        note = scale[0] if random.random() < 0.7 else scale[4 % len(scale)]
                    else:
                        # Any note from the scale
                        note = random.choice(scale)
                    
                    # For funky bass, occasionally add octave jumps
                    if is_funky and random.random() < 0.3:
                        note = note + (12 if random.random() < 0.5 else -12)
                    
                    # Ensure note is in a good bass range (E1 to E3)
                    while note < 28:  # E1
                        note += 12
                    while note > 52:  # E3
                        note -= 12
                    
                    # Determine velocity (louder for funky bass)
                    velocity_min = 90 if is_funky else 70
                    velocity_max = 120 if is_funky else 110
                    velocity = random.randint(velocity_min, velocity_max)
                    
                    # Calculate timing
                    time = (bar * beats_per_bar + beat) * TICKS_PER_BEAT + note_idx * ticks_per_note
                    
                    # Determine duration (shorter for funky bass to create more staccato feel)
                    if is_funky:
                        duration_factor = random.uniform(0.5, 0.8)
                    else:
                        duration_factor = random.uniform(0.8, 1.0)
                    
                    duration = int(ticks_per_note * duration_factor)
                    
                    bass_line.append((note, velocity, time, duration))
    
    return bass_line

def generate_chord_progression(root_note, scale_type, num_bars, beats_per_bar):
    """Generate a chord progression based on the root note and scale."""
    scale = get_scale_notes(root_note, scale_type)
    chord_progression = []
    
    # Common chord progressions in the scale
    if scale_type == MAJOR_SCALE:
        # I-IV-V-I, I-vi-IV-V, etc.
        possible_progressions = [
            [0, 3, 4, 0],  # I-IV-V-I
            [0, 5, 3, 4],  # I-vi-IV-V
            [0, 3, 5, 4],  # I-IV-vi-V
            [0, 5, 0, 4]   # I-vi-I-V
        ]
    else:  # Minor or other scales
        # i-iv-v-i, i-VI-III-VII, etc.
        possible_progressions = [
            [0, 3, 4, 0],  # i-iv-v-i
            [0, 5, 2, 6],  # i-VI-III-VII
            [0, 5, 3, 4],  # i-VI-iv-v
            [0, 2, 5, 0]   # i-III-VI-i
        ]
    
    # Choose a progression
    progression_indices = random.choice(possible_progressions)
    
    # Determine chord types based on scale
    if scale_type == MAJOR_SCALE:
        chord_types = [MAJOR_TRIAD, MINOR_TRIAD, MINOR_TRIAD, MAJOR_TRIAD, MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD]
    else:  # Minor or other scales
        chord_types = [MINOR_TRIAD, DIMINISHED_TRIAD, MAJOR_TRIAD, MINOR_TRIAD, MINOR_TRIAD, MAJOR_TRIAD, MAJOR_TRIAD]
    
    # Generate chords for each bar
    for bar in range(num_bars):
        # Determine which chord to use for this bar
        progression_idx = progression_indices[bar % len(progression_indices)]
        scale_degree = progression_idx
        chord_root = scale[scale_degree]
        chord_type = chord_types[scale_degree]
        
        # Get the notes for this chord
        chord_notes = get_chord_notes(chord_root, chord_type)
        
        # Add chord at the beginning of the bar
        time = bar * beats_per_bar * TICKS_PER_BEAT
        
        # Determine voicing and rhythm
        if random.random() < 0.7:
            # Block chord
            duration = beats_per_bar * TICKS_PER_BEAT
            for note in chord_notes:
                # Ensure note is in a good range for chords (middle of the keyboard)
                while note < 48:  # C3
                    note += 12
                while note > 72:  # C5
                    note -= 12
                velocity = random.randint(100, 125)
                chord_progression.append((note, velocity, time, duration))
        else:
            # Arpeggiated chord
            notes_per_beat = 2  # Eighth notes
            ticks_per_note = TICKS_PER_BEAT // notes_per_beat
            
            for beat in range(beats_per_bar):
                for note_idx in range(notes_per_beat):
                    if random.random() < 0.8:  # 80% chance to play a note
                        note = random.choice(chord_notes)
                        # Ensure note is in a good range
                        while note < 48:  # C3
                            note += 12
                        while note > 72:  # C5
                            note -= 12
                        velocity = random.randint(100, 120)
                        note_time = time + beat * TICKS_PER_BEAT + note_idx * ticks_per_note
                        duration = int(ticks_per_note * random.uniform(0.8, 1.0))
                        chord_progression.append((note, velocity, note_time, duration))
    
    return chord_progression