"""
Music theory utilities for the procedural music generation system.
Provides scales, chords, and other music theory concepts.
"""

import numpy as np
import random
import pretty_midi

# Define musical constants
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Scale definitions (intervals from root note)
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # Whole, Whole, Half, Whole, Whole, Whole, Half
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]  # Whole, Half, Whole, Whole, Half, Whole, Whole
HARMONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 11]  # Adds raised 7th to natural minor
MELODIC_MINOR_SCALE = [0, 2, 3, 5, 7, 9, 11]  # Raised 6th and 7th when ascending
PENTATONIC_MAJOR_SCALE = [0, 2, 4, 7, 9]  # Five-note scale derived from major scale
PENTATONIC_MINOR_SCALE = [0, 3, 5, 7, 10]  # Five-note scale derived from minor scale
BLUES_SCALE = [0, 3, 5, 6, 7, 10]  # Minor pentatonic with added blue note
DORIAN_MODE = [0, 2, 3, 5, 7, 9, 10]  # Minor scale with raised 6th
PHRYGIAN_MODE = [0, 1, 3, 5, 7, 8, 10]  # Minor scale with lowered 2nd
LYDIAN_MODE = [0, 2, 4, 6, 7, 9, 11]  # Major scale with raised 4th
MIXOLYDIAN_MODE = [0, 2, 4, 5, 7, 9, 10]  # Major scale with lowered 7th
LOCRIAN_MODE = [0, 1, 3, 5, 6, 8, 10]  # Diminished scale

# Chord definitions (intervals from root note)
MAJOR_TRIAD = [0, 4, 7]  # Root, Major 3rd, Perfect 5th
MINOR_TRIAD = [0, 3, 7]  # Root, Minor 3rd, Perfect 5th
DIMINISHED_TRIAD = [0, 3, 6]  # Root, Minor 3rd, Diminished 5th
AUGMENTED_TRIAD = [0, 4, 8]  # Root, Major 3rd, Augmented 5th
MAJOR_SEVENTH = [0, 4, 7, 11]  # Major triad with major 7th
DOMINANT_SEVENTH = [0, 4, 7, 10]  # Major triad with minor 7th
MINOR_SEVENTH = [0, 3, 7, 10]  # Minor triad with minor 7th
HALF_DIMINISHED_SEVENTH = [0, 3, 6, 10]  # Diminished triad with minor 7th
DIMINISHED_SEVENTH = [0, 3, 6, 9]  # Diminished triad with diminished 7th

# Chord types and their intervals
CHORD_TYPES = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'diminished': [0, 3, 6],
    'augmented': [0, 4, 8],
    'dominant7': [0, 4, 7, 10],
    'major7': [0, 4, 7, 11],
    'minor7': [0, 3, 7, 10],
    'half_diminished7': [0, 3, 6, 10],
    'diminished7': [0, 3, 6, 9],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7]
}

# Common chord progressions by type
PROGRESSIONS = {
    "pop": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "V"],
        ["vi", "IV", "I", "V"],
        ["I", "V", "IV", "V"]
    ],
    "jazz": [
        ["ii", "V", "I"],
        ["I", "vi", "ii", "V"],
        ["iii", "VI", "ii", "V", "I"],
        ["I", "IV", "iii", "VI", "ii", "V"]
    ],
    "classical": [
        ["I", "IV", "V", "I"],
        ["I", "ii", "V", "I"],
        ["I", "vi", "IV", "V"],
        ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]
    ]
}

# Roman numeral to scale degree mapping
ROMAN_TO_SCALE_DEGREE = {
    "I": 0, "i": 0,
    "II": 1, "ii": 1,
    "III": 2, "iii": 2,
    "IV": 3, "iv": 3,
    "V": 4, "v": 4,
    "VI": 5, "vi": 5,
    "VII": 6, "vii": 6
}

# Roman numeral to chord type mapping
ROMAN_TO_CHORD_TYPE = {
    "I": "major", "i": "minor",
    "II": "major", "ii": "minor",
    "III": "major", "iii": "minor",
    "IV": "major", "iv": "minor",
    "V": "major", "v": "minor",
    "VI": "major", "vi": "minor",
    "VII": "major", "vii": "diminished"
}

# Common drum patterns by complexity
DRUM_PATTERNS = {
    "simple": {
        "kick": [1, 0, 0, 0, 1, 0, 0, 0],
        "snare": [0, 0, 1, 0, 0, 0, 1, 0],
        "hihat": [1, 1, 1, 1, 1, 1, 1, 1]
    },
    "medium": {
        "kick": [1, 0, 0, 1, 1, 0, 0, 0],
        "snare": [0, 0, 1, 0, 0, 0, 1, 0],
        "hihat": [1, 1, 1, 1, 1, 1, 1, 1],
        "ride": [0, 1, 0, 1, 0, 1, 0, 1]
    },
    "complex": {
        "kick": [1, 0, 0, 1, 0, 1, 0, 0],
        "snare": [0, 0, 1, 0, 0, 0, 1, 1],
        "hihat": [1, 1, 1, 1, 1, 1, 1, 1],
        "ride": [0, 1, 0, 1, 0, 1, 0, 1],
        "tom": [0, 0, 0, 0, 0, 0, 1, 0]
    }
}

# MIDI note numbers for drum kit
DRUM_NOTES = {
    "kick": 36,
    "snare": 38,
    "hihat": 42,
    "ride": 51,
    "tom": 45
}

def get_scale_notes(root_note, scale_type):
    """
    Generate a list of MIDI note numbers for a scale starting from the root note.
    
    Args:
        root_note (int): MIDI note number of the root note
        scale_type (list): List of intervals defining the scale
        
    Returns:
        list: List of MIDI note numbers in the scale
    """
    # Ensure root_note is an integer
    root_note = int(root_note)
    
    # Generate scale notes for 3 octaves
    scale_notes = []
    for octave in range(-1, 2):  # -1, 0, 1 (for lower, middle, and upper octaves)
        for interval in scale_type:
            interval = int(interval)
            note = root_note + interval + (octave * 12)
            if 0 <= note <= 127:  # Valid MIDI note range
                scale_notes.append(note)
    
    return sorted(scale_notes)


def get_chord_from_scale(scale, scale_degree, chord_type=None):
    """
    Get a chord from a scale based on the scale degree.
    
    Args:
        scale (list): List of scale notes
        scale_degree (int): Degree of the scale to build the chord on (1-based)
        chord_type (list, optional): List of intervals defining the chord type.
                                    If None, use the diatonic chord.
        
    Returns:
        list: List of MIDI note numbers in the chord
    """
    # Adjust scale_degree to be 0-based
    scale_degree = (scale_degree - 1) % len(scale)
    
    # Get the root note of the chord
    root_note = scale[scale_degree]
    
    # If chord_type is specified, use it
    if chord_type:
        chord_notes = [root_note + interval for interval in chord_type]
        # Filter out notes that are out of MIDI range
        chord_notes = [note for note in chord_notes if 0 <= note <= 127]
        return chord_notes
    
    # Otherwise, build a diatonic chord (1-3-5-7)
    chord_notes = []
    
    # Add the root note
    chord_notes.append(root_note)
    
    # Add the third (2 scale degrees up)
    third_degree = (scale_degree + 2) % len(scale)
    third_note = scale[third_degree]
    # Ensure the third is in the same or next octave
    while third_note < root_note:
        third_note += 12
    chord_notes.append(third_note)
    
    # Add the fifth (4 scale degrees up)
    fifth_degree = (scale_degree + 4) % len(scale)
    fifth_note = scale[fifth_degree]
    # Ensure the fifth is in the same or next octave
    while fifth_note < root_note:
        fifth_note += 12
    chord_notes.append(fifth_note)
    
    # Add the seventh for seventh chords (6 scale degrees up)
    seventh_degree = (scale_degree + 6) % len(scale)
    seventh_note = scale[seventh_degree]
    # Ensure the seventh is in the same or next octave
    while seventh_note < root_note:
        seventh_note += 12
    chord_notes.append(seventh_note)
    
    return chord_notes



def get_chord_notes(root_note, chord_type):
    """
    Generate a list of MIDI note numbers for a chord starting from the root note.
    
    Args:
        root_note (int): MIDI note number of the root note
        chord_type (list): List of intervals defining the chord
        
    Returns:
        list: List of MIDI note numbers in the chord
    """
    # Ensure root_note is an integer
    root_note = int(root_note)
    
    # Generate chord notes
    chord_notes = []
    for interval in chord_type:
        note = root_note + interval
        if 0 <= note <= 127:  # Valid MIDI note range
            chord_notes.append(note)
    
    return chord_notes

# Get a chord progression based on key and type
def get_chord_progression(root_note, scale_type=MAJOR_SCALE, progression_type="pop", num_bars=16):
    """
    Generate a chord progression based on key, scale type, and progression style.
    
    Args:
        key: Integer representing the root note (0-11 for C to B)
        scale_type: "major" or "minor"
        progression_type: "pop", "jazz", or "classical"
        num_bars: Number of bars in the progression
        
    Returns:
        List of chords, where each chord is a list of MIDI note numbers
    """
    # Get scale degrees based on scale type
    #scale_degrees = MAJOR_SCALE if scale_type == "major" else MINOR_SCALE
    
    # Select a progression pattern
    progression_patterns = PROGRESSIONS[progression_type]
    pattern = random.choice(progression_patterns)
    
    # Extend pattern to fill required number of bars
    extended_pattern = []
    while len(extended_pattern) < num_bars:
        extended_pattern.extend(pattern)
    extended_pattern = extended_pattern[:num_bars]
    
    # Convert Roman numerals to actual chords
    chords = []
    for numeral in extended_pattern:
        # Get scale degree
        scale_degree = ROMAN_TO_SCALE_DEGREE[numeral]
        
        # Get chord type
        chord_type = ROMAN_TO_CHORD_TYPE[numeral]
        
        # Calculate root note
        #root = (key + scale_degrees[scale_degree]) % 12
        
        # Get chord intervals
        intervals = CHORD_TYPES[chord_type]
        
        # Create chord
        #chord = [root + interval for interval in intervals]
        
        #chords.append(chord)
        
        scale = get_scale_notes(root_note, scale_type)
    
        # Filter to just one octave of the scale
        one_octave = [note for note in scale if root_note <= note < root_note + 12]
        
        # Adjust for 1-based indexing and handle out-of-range degrees
        degree_idx = (scale_degree) % len(one_octave)
        
        # Get the root note for this chord
        chord_root = one_octave[degree_idx]
        
        # Determine chord type based on scale degree
        if scale_type == MAJOR_SCALE:
            if scale_degree in [0, 3, 4]:  # I, IV, V are major
                chord = get_chord_notes(chord_root, MAJOR_TRIAD)
            elif scale_degree in [1, 2, 5]:  # ii, iii, vi are minor
                chord = get_chord_notes(chord_root, MINOR_TRIAD)
            else:  # vii° is diminished
                chord = get_chord_notes(chord_root, DIMINISHED_TRIAD)
        elif scale_type == MINOR_SCALE:
            if scale_degree in [2, 5, 6]:  # III, VI, VII are major
                chord = get_chord_notes(chord_root, MAJOR_TRIAD)
            elif scale_degree in [0, 3, 4]:  # i, iv, v are minor
                chord = get_chord_notes(chord_root, MINOR_TRIAD)
            else:  # ii° is diminished
                chord = get_chord_notes(chord_root, DIMINISHED_TRIAD)
        else:
            # Default to major triad if scale type is not recognized
            chord = get_chord_notes(chord_root, MAJOR_TRIAD)
        
        chords.append(chord)
    
    return chords

def get_note_name(midi_note):
    """
    Convert a MIDI note number to a note name (e.g., C4, F#5).
    
    Args:
        midi_note (int): MIDI note number
        
    Returns:
        str: Note name with octave
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note = note_names[midi_note % 12]
    return f"{note}{octave}"

def get_midi_note(note_name):
    """
    Convert a note name to a MIDI note number.
    
    Args:
        note_name (str): Note name with octave (e.g., C4, F#5)
        
    Returns:
        int: MIDI note number
    """
    note_names = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 
                 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 
                 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    
    # Extract note and octave
    if len(note_name) < 2:
        return None
    
    if note_name[1] == '#' or note_name[1] == 'b':
        if len(note_name) < 3:
            return None
        note = note_name[0:2]
        octave = int(note_name[2:])
    else:
        note = note_name[0]
        octave = int(note_name[1:])
    
    # Calculate MIDI note number
    if note in note_names:
        return note_names[note] + ((octave + 1) * 12)
    else:
        return None

def is_note_in_scale(note, scale):
    """
    Check if a note is in a given scale.
    
    Args:
        note (int): MIDI note number to check
        scale (list): List of MIDI note numbers in the scale
        
    Returns:
        bool: True if the note is in the scale, False otherwise
    """
    # Get the pitch class (0-11) of the note
    pitch_class = note % 12
    
    # Check if any note in the scale has the same pitch class
    for scale_note in scale:
        if scale_note % 12 == pitch_class:
            return True
    
    return False

def get_nearest_scale_note(note, scale):
    """
    Find the nearest note in a scale to a given note.
    
    Args:
        note (int): MIDI note number to find the nearest scale note for
        scale (list): List of MIDI note numbers in the scale
        
    Returns:
        int: MIDI note number of the nearest scale note
    """
    if is_note_in_scale(note, scale):
        return note
    
    # Find the nearest note in the scale
    nearest_note = None
    min_distance = float('inf')
    
    for scale_note in scale:
        distance = abs(note - scale_note)
        if distance < min_distance:
            min_distance = distance
            nearest_note = scale_note
    
    return nearest_note

def get_scale_degree(note, scale):
    """
    Get the scale degree (1-7) of a note in a scale.
    
    Args:
        note (int): MIDI note number
        scale (list): List of MIDI note numbers in the scale
        
    Returns:
        int: Scale degree (1-7) or None if the note is not in the scale
    """
    # Get the pitch class (0-11) of the note
    pitch_class = note % 12
    
    # Get the pitch classes of the scale notes (one octave)
    scale_pitch_classes = [scale_note % 12 for scale_note in scale]
    scale_pitch_classes = sorted(list(set(scale_pitch_classes)))  # Remove duplicates
    
    # Find the scale degree
    if pitch_class in scale_pitch_classes:
        return scale_pitch_classes.index(pitch_class) + 1
    else:
        return None

def transpose_to_key(notes, from_key, to_key):
    """
    Transpose a list of notes from one key to another.
    
    Args:
        notes (list): List of MIDI note numbers
        from_key (int): MIDI note number of the current key's root note
        to_key (int): MIDI note number of the target key's root note
        
    Returns:
        list: List of transposed MIDI note numbers
    """
    # Calculate the transposition interval
    interval = to_key - from_key
    
    # Transpose each note
    transposed_notes = [note + interval for note in notes]
    
    # Ensure all notes are in the valid MIDI range (0-127)
    transposed_notes = [note for note in transposed_notes if 0 <= note <= 127]
    
    return transposed_notes

def get_common_chord_progressions(style='pop'):
    """
    Get common chord progressions for different musical styles.
    
    Args:
        style (str): Musical style ('pop', 'rock', 'jazz', 'classical', 'blues')
        
    Returns:
        list: List of common chord progressions as scale degrees
    """
    progressions = {
        'pop': [
            [1, 5, 6, 4],  # I-V-vi-IV (most common pop progression)
            [1, 4, 5, 4],  # I-IV-V-IV
            [6, 4, 1, 5],  # vi-IV-I-V
            [1, 6, 4, 5],  # I-vi-IV-V (50s progression)
            [1, 5, 6, 3, 4, 1, 4, 5]  # I-V-vi-iii-IV-I-IV-V
        ],
        'rock': [
            [1, 4, 5],  # I-IV-V (classic rock)
            [1, 5, 6, 4],  # I-V-vi-IV
            [1, 6, 4, 5],  # I-vi-IV-V
            [1, 4, 6, 5],  # I-IV-vi-V
            [1, 3, 4, 6]   # I-iii-IV-vi
        ],
        'jazz': [
            [2, 5, 1],  # ii-V-I (most common jazz progression)
            [1, 6, 2, 5],  # I-vi-ii-V (rhythm changes)
            [1, 7, 3, 6, 2, 5, 1],  # I-vii-iii-vi-ii-V-I (circle of fifths)
            [6, 2, 5, 1],  # vi-ii-V-I
            [3, 6, 2, 5, 1]  # iii-vi-ii-V-I
        ],
        'classical': [
            [1, 4, 5, 1],  # I-IV-V-I (common classical cadence)
            [1, 4, 5, 6],  # I-IV-V-vi (deceptive cadence)
            [1, 6, 4, 5],  # I-vi-IV-V
            [1, 5, 6, 3, 4, 1, 4, 5],  # I-V-vi-iii-IV-I-IV-V
            [6, 5, 4, 3, 2, 1]  # vi-V-IV-III-II-I (descending progression)
        ],
        'blues': [
            [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5],  # 12-bar blues
            [1, 4, 1, 5, 4, 1],  # 8-bar blues
            [1, 4, 1, 5, 4, 1, 5],  # 16-bar blues
            [1, 6, 2, 5],  # I-vi-ii-V (jazz blues)
            [1, 3, 4, 5]  # I-iii-IV-V
        ],
        'trap': [
            [6, 5, 4, 5],  # vi-V-IV-V (minor progression common in trap)
            [6, 4, 5, 1],  # vi-IV-V-I
            [6, 4, 1, 5],  # vi-IV-I-V
            [1, 5, 6, 4],  # I-V-vi-IV
            [6, 5, 4, 1]   # vi-V-IV-I
        ],
        'phonk': [
            [6, 7, 1, 5],  # vi-vii-I-V (dark progression with diminished)
            [6, 4, 5, 6],  # vi-IV-V-vi (looping minor progression)
            [6, 5, 3, 4],  # vi-V-iii-IV
            [6, 3, 4, 1],  # vi-iii-IV-I
            [6, 7, 3, 5]   # vi-vii-iii-V
        ],
        'ambient': [
            [1, 4, 6, 5],  # I-IV-vi-V (dreamy progression)
            [1, 6, 3, 4],  # I-vi-iii-IV
            [6, 1, 5, 4],  # vi-I-V-IV
            [4, 1, 5, 6],  # IV-I-V-vi
            [1, 5, 6, 3]   # I-V-vi-iii
        ]
    }
    
    # Return progressions for the requested style, or pop if not found
    return progressions.get(style.lower(), progressions['pop'])

# Get a compatible scale for a melody
def get_compatible_scale(notes):
    """
    Analyze a set of notes and determine the most compatible scale.
    
    Args:
        notes: List of MIDI note numbers
        
    Returns:
        Tuple of (key, scale_type) where key is 0-11 (C to B) and scale_type is "major" or "minor"
    """
    # Convert notes to pitch classes (0-11)
    pitch_classes = [note % 12 for note in notes]
    
    # Count occurrences of each pitch class
    pc_counts = [0] * 12
    for pc in pitch_classes:
        pc_counts[pc] += 1
    
    # Try each possible key and scale type
    best_score = -1
    best_key = 0
    best_scale = "major"
    
    for key in range(12):
        # Check major scale
        major_score = 0
        for i, degree in enumerate(MAJOR_SCALE):
            pc = (key + degree) % 12
            # Give more weight to tonic, dominant, and subdominant
            weight = 3 if i in [0, 4] else (2 if i == 3 else 1)
            major_score += pc_counts[pc] * weight
        
        # Check minor scale
        minor_score = 0
        for i, degree in enumerate(MINOR_SCALE):
            pc = (key + degree) % 12
            # Give more weight to tonic, dominant, and subdominant
            weight = 3 if i in [0, 4] else (2 if i == 3 else 1)
            minor_score += pc_counts[pc] * weight
        
        # Update best if needed
        if major_score > best_score:
            best_score = major_score
            best_key = key
            best_scale = "major"
        
        if minor_score > best_score:
            best_score = minor_score
            best_key = key
            best_scale = "minor"
    
    return best_key, best_scale

# Generate a bassline based on chord progression
def generate_bassline(chord_progression, time_signature=(4, 4), tempo=120):
    """
    Generate a bassline based on a chord progression.
    
    Args:
        chord_progression: List of chords, where each chord is a list of MIDI note numbers
        time_signature: Tuple of (beats_per_bar, beat_unit)
        tempo: Tempo in BPM
        
    Returns:
        List of pretty_midi.Note objects representing the bassline
    """
    bassline = []
    
    beats_per_bar = time_signature[0]
    beat_duration = 60 / tempo  # in seconds
    bar_duration = beats_per_bar * beat_duration
    
    # Define some common bassline patterns
    patterns = [
        # Root on beat 1, fifth on beat 3
        lambda root: [
            (root, 0, 1),
            ((root + 7) % 12, 2, 1)
        ],
        # Root on beats 1 and 3
        lambda root: [
            (root, 0, 1),
            (root, 2, 1)
        ],
        # Walking bass (root, third, fifth, approach)
        lambda root: [
            (root, 0, 1),
            ((root + 4) % 12, 1, 1),
            ((root + 7) % 12, 2, 1),
            ((root - 1) % 12, 3, 1)
        ],
        # Arpeggiated pattern
        lambda root: [
            (root, 0, 0.5),
            ((root + 7) % 12, 0.5, 0.5),
            ((root + 4) % 12, 1, 0.5),
            (root, 1.5, 0.5),
            (root, 2, 0.5),
            ((root + 7) % 12, 2.5, 0.5),
            ((root + 4) % 12, 3, 0.5),
            (root, 3.5, 0.5)
        ]
    ]
    
    # Generate bassline for each bar
    for bar, chord in enumerate(chord_progression):
        # Get the root note
        root = chord[0]
        
        # Choose a pattern (with some continuity between bars)
        if bar > 0 and random.random() < 0.7:
            # 70% chance to keep the same pattern
            pattern_idx = bassline_pattern_idx
        else:
            pattern_idx = random.randint(0, len(patterns) - 1)
        
        bassline_pattern_idx = pattern_idx
        pattern = patterns[pattern_idx]
        
        # Generate notes for this bar
        for note_pc, beat_offset, duration in pattern(root):
            # Move to bass register (octave 2-3)
            pitch = note_pc + 36  # C2 = 36
            
            # Create note
            note = pretty_midi.Note(
                velocity=110,
                pitch=pitch,
                start=bar * bar_duration + beat_offset * beat_duration,
                end=bar * bar_duration + (beat_offset + duration) * beat_duration
            )
            
            bassline.append(note)
    
    return bassline

# Generate a rhythm pattern
def generate_rhythm_pattern(complexity="medium", time_signature=(4, 4), num_bars=16, tempo=120):
    """
    Generate a drum rhythm pattern.
    
    Args:
        complexity: "simple", "medium", or "complex"
        time_signature: Tuple of (beats_per_bar, beat_unit)
        num_bars: Number of bars
        tempo: Tempo in BPM
        
    Returns:
        List of pretty_midi.Note objects representing the drum pattern
    """
    pattern = DRUM_PATTERNS[complexity]
    
    beats_per_bar = time_signature[0]
    beat_duration = 60 / tempo  # in seconds
    bar_duration = beats_per_bar * beat_duration
    
    # Calculate steps per beat (8 steps per bar in our patterns)
    steps_per_bar = 8
    step_duration = bar_duration / steps_per_bar
    
    drum_notes = []
    
    # Add some variation every 4 bars
    for bar in range(num_bars):
        bar_start = bar * bar_duration
        
        # Introduce variations
        if bar % 4 == 3:  # Every 4th bar
            # Add a fill or variation
            if complexity == "simple":
                # Simple fill
                fill = {
                    "kick": [1, 0, 0, 0, 1, 0, 1, 1],
                    "snare": [0, 0, 1, 0, 0, 0, 1, 1],
                    "hihat": [1, 1, 1, 1, 1, 1, 0, 0]
                }
            elif complexity == "medium":
                # Medium fill
                fill = {
                    "kick": [1, 0, 0, 1, 0, 0, 1, 0],
                    "snare": [0, 0, 1, 0, 1, 1, 0, 1],
                    "hihat": [1, 1, 0, 0, 0, 0, 0, 0],
                    "ride": [0, 0, 0, 0, 0, 0, 0, 0],
                    "tom": [0, 0, 0, 0, 1, 1, 1, 1]
                }
            else:  # complex
                # Complex fill
                fill = {
                    "kick": [1, 0, 1, 0, 1, 0, 0, 0],
                    "snare": [0, 0, 0, 0, 0, 1, 1, 1],
                    "hihat": [0, 0, 0, 0, 0, 0, 0, 0],
                    "ride": [0, 0, 0, 0, 0, 0, 0, 0],
                    "tom": [0, 1, 0, 1, 1, 1, 1, 1]
                }
            
            # Use the fill for this bar
            for drum_type, rhythm in fill.items():
                if drum_type in DRUM_NOTES:
                    note_number = DRUM_NOTES[drum_type]
                    
                    for step, hit in enumerate(rhythm):
                        if hit:
                            note = pretty_midi.Note(
                                velocity=100 if drum_type == "kick" or drum_type == "snare" else 80,
                                pitch=note_number,
                                start=bar_start + step * step_duration,
                                end=bar_start + step * step_duration + step_duration
                            )
                            drum_notes.append(note)
        else:
            # Use the standard pattern
            for drum_type, rhythm in pattern.items():
                if drum_type in DRUM_NOTES:
                    note_number = DRUM_NOTES[drum_type]
                    
                    for step, hit in enumerate(rhythm):
                        if hit:
                            note = pretty_midi.Note(
                                velocity=100 if drum_type == "kick" or drum_type == "snare" else 80,
                                pitch=note_number,
                                start=bar_start + step * step_duration,
                                end=bar_start + step * step_duration + step_duration
                            )
                            drum_notes.append(note)
    
    return drum_notes

# Harmonize a melody with a chord progression
def harmonize_melody(melody_notes, chord_progression, time_signature=(4, 4), tempo=120, method="rule_based"):
    """
    Harmonize a melody with a chord progression.
    
    Args:
        melody_notes: List of pretty_midi.Note objects representing the melody
        chord_progression: List of chords, where each chord is a list of MIDI note numbers
        time_signature: Tuple of (beats_per_bar, beat_unit)
        tempo: Tempo in BPM
        method: "rule_based" or "ml_based"
        
    Returns:
        List of pretty_midi.Note objects representing the harmony
    """
    harmony_notes = []
    
    beats_per_bar = time_signature[0]
    beat_duration = 60 / tempo  # in seconds
    bar_duration = beats_per_bar * beat_duration
    
    if method == "rule_based":
        # Simple block chord approach with some rhythmic variation
        for bar, chord in enumerate(chord_progression):
            bar_start = bar * bar_duration
            bar_end = (bar + 1) * bar_duration
            
            # Find melody notes in this bar
            bar_melody_notes = [note for note in melody_notes 
                               if note.start >= bar_start and note.start < bar_end]
            
            # Determine chord voicing (inversion and register)
            # Move to middle register (octave 4-5)
            chord_pitches = [pitch + 60 for pitch in chord]  # C4 = 60
            
            # Apply different rhythmic patterns based on bar position
            if bar % 4 == 0:  # First bar of phrase
                # Whole note
                for pitch in chord_pitches[1:]:  # Skip root (bassline has it)
                    note = pretty_midi.Note(
                        velocity=90,
                        pitch=pitch,
                        start=bar_start,
                        end=bar_end
                    )
                    harmony_notes.append(note)
            
            elif bar % 4 == 3:  # Last bar of phrase
                # Rhythmic pattern
                for beat in range(beats_per_bar):
                    beat_start = bar_start + beat * beat_duration
                    
                    # Different pattern for last beat
                    if beat == beats_per_bar - 1:
                        # Eighth notes
                        for i in range(2):
                            for pitch in chord_pitches[1:]:
                                note = pretty_midi.Note(
                                    velocity=90,
                                    pitch=pitch,
                                    start=beat_start + i * beat_duration/2,
                                    end=beat_start + (i+1) * beat_duration/2
                                )
                                harmony_notes.append(note)
                    else:
                        # Quarter note
                        for pitch in chord_pitches[1:]:
                            note = pretty_midi.Note(
                                velocity=90,
                                pitch=pitch,
                                start=beat_start,
                                end=beat_start + beat_duration
                            )
                            harmony_notes.append(note)
            
            else:  # Middle bars of phrase
                # Half notes
                for half in range(2):
                    half_start = bar_start + half * bar_duration/2
                    
                    for pitch in chord_pitches[1:]:
                        note = pretty_midi.Note(
                            velocity=80,
                            pitch=pitch,
                            start=half_start,
                            end=half_start + bar_duration/2
                        )
                        harmony_notes.append(note)
    
    elif method == "ml_based":
        # This would be where you'd implement ML-based harmonization
        # For now, we'll use a slightly more advanced rule-based approach
        
        # Analyze melody to find important notes
        for bar in range(len(chord_progression)):
            chord = chord_progression[bar]
            bar_start = bar * bar_duration
            bar_end = (bar + 1) * bar_duration
            
            # Find melody notes in this bar
            bar_melody_notes = [note for note in melody_notes 
                               if note.start >= bar_start and note.start < bar_end]
            
            if not bar_melody_notes:
                # If no melody notes, just add block chord
                chord_pitches = [pitch + 60 for pitch in chord]  # C4 = 60
                
                for pitch in chord_pitches[1:]:
                    chord_note = pretty_midi.Note(
                        velocity=80,
                        pitch=pitch,
                        start=bar_start,
                        end=bar_end
                    )
                    harmony_notes.append(chord_note)
            else:
                # Find important beats in the bar
                important_beats = [0, beats_per_bar // 2]  # First beat and middle beat
                
                # Move to middle register
                chord_pitches = [pitch + 60 for pitch in chord]  # C4 = 60
                
                for beat in important_beats:
                    beat_time = bar_start + beat * beat_duration
                    
                    # Add chord notes
                    for pitch in chord_pitches[1:]:
                        chord_note = pretty_midi.Note(
                            velocity=80,
                            pitch=pitch,
                            start=beat_time,
                            end=beat_time + beat_duration
                        )
                        harmony_notes.append(chord_note)
                
                # Add some counterpoint based on melody
                for note in bar_melody_notes:
                    # Find a compatible harmony note
                    melody_pitch_class = note.pitch % 12
                    
                    # Check if melody note is in chord
                    chord_pcs = [p % 12 for p in chord]
                    
                    if melody_pitch_class not in chord_pcs:
                        # Find closest chord tone
                        closest_pc = min(chord_pcs, key=lambda pc: min((melody_pitch_class - pc) % 12, (pc - melody_pitch_class) % 12))
                        
                        # Create a harmony note a third or sixth below
                        harmony_pc = (melody_pitch_class - 4) % 12  # Third below
                        
                        if harmony_pc not in chord_pcs:
                            harmony_pc = (melody_pitch_class - 9) % 12  # Sixth below
                        
                        # Find octave (1 octave below melody)
                        harmony_pitch = ((note.pitch // 12) - 1) * 12 + harmony_pc
                        
                        # Create harmony note
                        harmony_note = pretty_midi.Note(
                            velocity=80,
                            pitch=harmony_pitch,
                            start=note.start,
                            end=note.end
                        )
                        
                        harmony_notes.append(harmony_note)
    
    return harmony_notes

# Analyze a melody to determine key and structure
def analyze_melody(melody_notes):
    """
    Analyze a melody to determine key, scale, and structure.
    
    Args:
        melody_notes: List of pretty_midi.Note objects
        
    Returns:
        Dictionary with analysis results
    """
    if not melody_notes:
        return {"key": 60, "scale_type": "major", "note_count": {}}
    
    # Sort notes by start time
    melody_notes.sort(key=lambda x: x.start)
    
    # Count occurrences of each pitch class
    pitch_class_count = [0] * 12
    for note in melody_notes:
        pitch_class = note.pitch % 12
        pitch_class_count[pitch_class] += 1
    
    # Find the most common pitch class (potential key)
    max_count = max(pitch_class_count)
    potential_keys = [i for i, count in enumerate(pitch_class_count) if count == max_count]
    
    # For simplicity, just take the first potential key
    key = potential_keys[0]
    
    # Determine if major or minor
    # This is a simplified approach - in reality, key detection is more complex
    major_key_score = 0
    minor_key_score = 0
    
    # Check major scale notes
    for i, pc in enumerate(MAJOR_SCALE):
        major_key_score += pitch_class_count[(key + pc) % 12]
    
    # Check minor scale notes
    for i, pc in enumerate(MINOR_SCALE):
        minor_key_score += pitch_class_count[(key + pc) % 12]
    
    scale_type = "major" if major_key_score >= minor_key_score else "minor"
    
    # Analyze phrase structure
    phrases = []
    current_phrase = []
    
    for i, note in enumerate(melody_notes):
        current_phrase.append(note)
        
        # Check for phrase ending
        if i < len(melody_notes) - 1:
            next_note = melody_notes[i + 1]
            gap = next_note.start - note.end
            
            # If there's a significant gap or a long note followed by a rest
            if gap > 1.0 or (note.end - note.start > 1.5 and gap > 0.5):
                phrases.append(current_phrase)
                current_phrase = []
    
    # Add the last phrase if not empty
    if current_phrase:
        phrases.append(current_phrase)
    
    return {
        "key": key,
        "scale_type": scale_type,
        "note_count": pitch_class_count,
        "phrases": phrases
    }

# Generate a compatible melody from scratch
def generate_melody(key, scale_type="major", num_bars=16, time_signature=(4, 4), tempo=120):
    """
    Generate a melody from scratch based on key and scale.
    
    Args:
        key: Integer representing the root note (0-11 for C to B)
        scale_type: "major" or "minor"
        num_bars: Number of bars
        time_signature: Tuple of (beats_per_bar, beat_unit)
        tempo: Tempo in BPM
        
    Returns:
        List of pretty_midi.Note objects representing the melody
    """
    # Get scale degrees
    scale_degrees = MAJOR_SCALE if scale_type == "major" else MINOR_SCALE
    
    # Create scale pitches (in middle octave)
    scale_pitches = [(key + degree) % 12 + 60 for degree in scale_degrees]
    
    # Add octave above and below
    scale_pitches_low = [(key + degree) % 12 + 48 for degree in scale_degrees]
    scale_pitches_high = [(key + degree) % 12 + 72 for degree in scale_degrees]
    all_scale_pitches = scale_pitches_low + scale_pitches + scale_pitches_high
    
    # Calculate timing
    beats_per_bar = time_signature[0]
    beat_duration = 60 / tempo  # in seconds
    bar_duration = beats_per_bar * beat_duration
    
    # Define some common rhythmic patterns (in beats)
    rhythmic_patterns = [
        [1.0],  # Quarter note
        [0.5, 0.5],  # Two eighth notes
        [0.75, 0.25],  # Dotted eighth + sixteenth
        [0.25, 0.75],  # Sixteenth + dotted eighth
        [0.5, 0.25, 0.25],  # Eighth + two sixteenths
        [0.25, 0.25, 0.5],  # Two sixteenths + eighth
        [0.25, 0.25, 0.25, 0.25]  # Four sixteenths
    ]
    
    # Define some common melodic patterns (scale degree movements)
    melodic_patterns = [
        [0, 1, 2],  # Ascending step
        [0, 2, 4],  # Ascending triad
        [0, -1, -2],  # Descending step
        [0, -2, -4],  # Descending triad
        [0, 1, 0, -1],  # Neighbor tones
        [0, 2, 1, 0],  # Turn
        [0, -2, -1, 0],  # Reverse turn
        [0, 4, 0],  # Arpeggiation
        [0, 7, 0]  # Octave leap
    ]
    
    melody_notes = []
    current_time = 0.0
    current_scale_idx = 7  # Start on the tonic in middle octave
    
    # Generate melody phrase by phrase
    num_phrases = num_bars // 4
    
    for phrase in range(num_phrases):
        phrase_start = current_time
        
        # Decide if this phrase is a repetition
        is_repetition = phrase > 0 and random.random() < 0.3
        
        if is_repetition:
            # Find notes from a previous phrase
            phrase_to_repeat = random.randint(0, phrase - 1)
            start_time = phrase_to_repeat * 4 * bar_duration
            end_time = start_time + 4 * bar_duration
            
            # Get notes from that phrase
            phrase_notes = [note for note in melody_notes 
                           if note.start >= start_time and note.start < end_time]
            
            # Copy them to current position
            for note in phrase_notes:
                new_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.start - start_time + current_time,
                    end=note.end - start_time + current_time
                )
                melody_notes.append(new_note)
            
            # Update current time
            current_time += 4 * bar_duration
        else:
            # Generate new phrase
            for bar in range(4):  # 4 bars per phrase
                bar_start = current_time
                beats_remaining = beats_per_bar
                
                while beats_remaining > 0:
                    # Choose a rhythmic pattern that fits
                    suitable_patterns = [p for p in rhythmic_patterns if sum(p) <= beats_remaining]
                    
                    if not suitable_patterns:
                        # No pattern fits, just use a single note
                        rhythm = [beats_remaining]
                    else:
                        rhythm = random.choice(suitable_patterns)
                    
                    # Choose a melodic pattern
                    melody_pattern = random.choice(melodic_patterns)
                    
                    # Apply the patterns
                    for i, (rhythm_val, degree_change) in enumerate(zip(rhythm, melody_pattern)):
                        # Update scale index
                        new_scale_idx = current_scale_idx + degree_change
                        
                        # Keep within range
                        while new_scale_idx < 0:
                            new_scale_idx += 7
                        while new_scale_idx >= len(all_scale_pitches):
                            new_scale_idx -= 7
                        
                        current_scale_idx = new_scale_idx
                        
                        # Create note
                        note = pretty_midi.Note(
                            velocity=90,
                            pitch=all_scale_pitches[current_scale_idx],
                            start=current_time,
                            end=current_time + rhythm_val * beat_duration
                        )
                        
                        melody_notes.append(note)
                        current_time += rhythm_val * beat_duration
                    
                    beats_remaining -= sum(rhythm)
                
                # Add a rest occasionally
                if random.random() < 0.2 and bar < 3:  # Not on the last bar of phrase
                    rest_duration = random.choice([0.5, 1.0]) * beat_duration
                    current_time += rest_duration
            
            # Make sure we're at the end of the phrase
            current_time = phrase_start + 4 * bar_duration
    
    return melody_notes

if __name__ == "__main__":
    # Example usage
    key = 0  # C
    scale = "major"
    
    # Generate a chord progression
    chords = get_chord_progression(key, scale, "pop", 8)
    print("Chord progression:", chords)
    
    # Generate a bassline
    bassline = generate_bassline(chords)
    print(f"Generated {len(bassline)} bass notes")
    
    # Generate a rhythm pattern
    rhythm = generate_rhythm_pattern("medium", num_bars=8)
    print(f"Generated {len(rhythm)} drum hits")
    
    # Generate a melody
    melody = generate_melody(key, scale, num_bars=8)
    print(f"Generated {len(melody)} melody notes")
    
    # Harmonize the melody
    harmony = harmonize_melody(melody, chords)
    print(f"Generated {len(harmony)} harmony notes")