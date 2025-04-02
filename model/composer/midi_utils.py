"""
MIDI utility functions for the procedural music generation system.
Provides functions for creating and manipulating MIDI files and notes.
"""

import mido
import random
import numpy as np

# Constants
TICKS_PER_BEAT = 480  # Standard MIDI resolution (480 PPQ)

def create_midi_file(tempo=120, time_signature=(4, 4)):
    """
    Create a new MIDI file with a single track.
    
    Args:
        filename (str): Output filename
        tempo (int): Tempo in BPM
        
    Returns:
        tuple: (MidiFile, MidiTrack) objects
    """
    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = mid.add_track()
    
    # Set tempo
    tempo_us = mido.bpm2tempo(tempo)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo_us, time=0))
    
    return mid, track

def add_note(track, note, velocity, time, duration, channel=0):
    """
    Add a note to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track to add the note to
        note (int): MIDI note number
        velocity (int): Note velocity (0-127)
        time (int): Start time in ticks
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    # Ensure valid MIDI values and convert to integers
    note = max(0, min(127, int(note)))
    velocity = max(0, min(127, int(velocity)))
    time = int(time)  # Ensure time is an integer
    duration = int(duration)  # Ensure duration is an integer
    channel = max(0, min(15, int(channel)))
    
    # Add note_on and note_off messages
    track.append(mido.Message('note_on', note=note, velocity=velocity, time=time, channel=channel))
    track.append(mido.Message('note_off', note=note, velocity=0, time=time + duration, channel=channel))

def add_chord(track, notes, velocity, time, duration, channel=0):
    """
    Add a chord (multiple simultaneous notes) to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track to add the chord to
        notes (list): List of MIDI note numbers
        velocity (int): Note velocity (0-127)
        time (int): Start time in ticks
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    for note in notes:
        add_note(track, note, velocity, time, duration, channel)

def add_control_change(track, control, value, time, channel=0):
    """
    Add a control change message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track to add the control change to
        control (int): Control number (0-127)
        value (int): Control value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Ensure valid MIDI values
    control = max(0, min(127, int(control)))
    value = max(0, min(127, int(value)))
    time = int(time)  # Ensure time is an integer
    channel = max(0, min(15, int(channel)))
    
    # Add control change message
    track.append(mido.Message('control_change', control=control, value=value, time=time, channel=channel))

def transpose_melody(melody, octave_shift):
    """
    Transpose a melody by a number of octaves.
    
    Args:
        melody (list): List of (note, velocity, time, duration) tuples
        octave_shift (int): Number of octaves to shift (positive or negative)
        
    Returns:
        list: Transposed melody
    """
    transposed = []
    for note, velocity, time, duration in melody:
        # Transpose the note by the specified number of octaves
        new_note = note + (octave_shift * 12)
        
        # Ensure the note is within the valid MIDI range (0-127)
        if 0 <= new_note <= 127:
            transposed.append((new_note, velocity, time, duration))
        else:
            # Skip notes that would be out of range
            pass
    
    return transposed

def adjust_velocity(melody, factor):
    """
    Adjust the velocity of all notes in a melody by a factor.
    
    Args:
        melody (list): List of (note, velocity, time, duration) tuples
        factor (float): Velocity multiplier
        
    Returns:
        list: Melody with adjusted velocities
    """
    adjusted = []
    for note, velocity, time, duration in melody:
        # Adjust velocity by the factor
        new_velocity = int(velocity * factor)
        
        # Ensure velocity is within the valid MIDI range (1-127)
        new_velocity = max(1, min(127, new_velocity))
        
        adjusted.append((note, new_velocity, time, duration))
    
    return adjusted

def repeat_pattern(pattern, num_repeats, pattern_length):
    """
    Repeat a pattern multiple times.
    
    Args:
        pattern (list): List of (note, velocity, time, duration) tuples
        num_repeats (int): Number of times to repeat the pattern
        pattern_length (int): Length of the pattern in ticks
        
    Returns:
        list: Repeated pattern
    """
    repeated = []
    for i in range(num_repeats):
        for note, velocity, time, duration in pattern:
            # Offset the time by the pattern length for each repeat
            new_time = time + (i * pattern_length)
            repeated.append((note, velocity, new_time, duration))
    
    return repeated

def get_pattern_length_ticks(pattern):
    """
    Calculate the length of a pattern in ticks.
    
    Args:
        pattern (list): List of (note, velocity, time, duration) tuples
        
    Returns:
        int: Length of the pattern in ticks
    """
    if not pattern:
        return 0
    
    # Find the end time of the last note
    max_end_time = 0
    for note, velocity, time, duration in pattern:
        end_time = time + duration
        max_end_time = max(max_end_time, end_time)
    
    return max_end_time

def analyze_melody_octave(melody):
    """
    Analyze the average octave of a melody.
    
    Args:
        melody (list): List of (note, velocity, time, duration) tuples
        
    Returns:
        float: Average octave of the melody
    """
    if not melody:
        return 5  # Default to middle C octave
    
    # Calculate the average note value
    total_notes = 0
    note_count = 0
    for note, _, _, _ in melody:
        if isinstance(note, int):  # Ensure note is a valid MIDI note number
            total_notes += note
            note_count += 1
    
    if note_count == 0:
        return 5  # Default to middle C octave
    
    avg_note = total_notes / note_count
    
    # Convert to octave (MIDI note 60 = C4, so divide by 12 and subtract 1)
    avg_octave = (avg_note / 12) - 1
    
    return avg_octave

def apply_audio_effect_params(track, effect_params, channel):
    """
    Apply audio effect parameters to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track to apply effects to
        effect_params (dict): Dictionary of effect parameters
        channel (int): MIDI channel (0-15)
    """
    # MIDI CC numbers for common effects
    REVERB_CC = 91
    CHORUS_CC = 93
    DELAY_CC = 94
    FILTER_CUTOFF_CC = 74
    FILTER_RESONANCE_CC = 71
    DISTORTION_CC = 92  # Not standard, but often used
    
    # Apply each effect if specified
    if 'reverb' in effect_params:
        value = int(effect_params['reverb'] * 127)
        add_control_change(track, REVERB_CC, value, 0, channel)
    
    if 'chorus' in effect_params:
        value = int(effect_params['chorus'] * 127)
        add_control_change(track, CHORUS_CC, value, 0, channel)
    
    if 'delay' in effect_params:
        value = int(effect_params['delay'] * 127)
        add_control_change(track, DELAY_CC, value, 0, channel)
    
    if 'filter_cutoff' in effect_params:
        value = int(effect_params['filter_cutoff'] * 127)
        add_control_change(track, FILTER_CUTOFF_CC, value, 0, channel)
    
    if 'filter_resonance' in effect_params:
        value = int(effect_params['filter_resonance'] * 127)
        add_control_change(track, FILTER_RESONANCE_CC, value, 0, channel)
    
    if 'distortion' in effect_params:
        value = int(effect_params['distortion'] * 127)
        add_control_change(track, DISTORTION_CC, value, 0, channel)

def apply_effect_automation(track, cc_number, start_value, end_value, duration, start_time, channel=0):
    """
    Apply an automated effect change over time.
    
    Args:
        track (MidiTrack): MIDI track to apply automation to
        cc_number (int): Control change number
        start_value (int): Starting value (0-127)
        end_value (int): Ending value (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the automation
    steps = 16
    
    # Apply the automation in steps
    for i in range(steps):
        # Calculate the current value using linear interpolation
        t = i / (steps - 1)
        current_value = int(start_value + (end_value - start_value) * t)
        
        # Calculate the current time and ensure it's an integer
        current_time = int(start_time + int(t * duration))
        
        # Add the control change message
        add_control_change(track, cc_number, current_value, current_time, channel)

def apply_filter_sweep(track, start_cutoff, end_cutoff, resonance, duration, start_time, channel=0):
    """
    Apply a filter sweep effect.
    
    Args:
        track (MidiTrack): MIDI track to apply the filter sweep to
        start_cutoff (int): Starting cutoff value (0-127)
        end_cutoff (int): Ending cutoff value (0-127)
        resonance (int): Resonance value (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # MIDI CC numbers for filter parameters
    FILTER_CUTOFF_CC = 74
    FILTER_RESONANCE_CC = 71
    
    # Set the resonance
    add_control_change(track, FILTER_RESONANCE_CC, resonance, start_time, channel)
    
    # Apply the cutoff automation
    apply_effect_automation(track, FILTER_CUTOFF_CC, start_cutoff, end_cutoff, duration, start_time, channel)

def quantize_notes(notes, grid_size):
    """
    Quantize notes to a grid.
    
    Args:
        notes (list): List of (note, velocity, time, duration) tuples
        grid_size (int): Grid size in ticks
        
    Returns:
        list: Quantized notes
    """
    quantized = []
    for note, velocity, time, duration in notes:
        # Quantize the start time
        quantized_time = round(time / grid_size) * grid_size
        
        # Quantize the duration
        quantized_duration = round(duration / grid_size) * grid_size
        
        # Ensure minimum duration
        if quantized_duration < grid_size:
            quantized_duration = grid_size
        
        quantized.append((note, velocity, quantized_time, quantized_duration))
    
    return quantized

def humanize_notes(notes, timing_variation=10, velocity_variation=10):
    """
    Add human-like variations to notes.
    
    Args:
        notes (list): List of (note, velocity, time, duration) tuples
        timing_variation (int): Maximum timing variation in ticks
        velocity_variation (int): Maximum velocity variation
        
    Returns:
        list: Humanized notes
    """
    humanized = []
    for note, velocity, time, duration in notes:
        # Add slight timing variation
        humanized_time = time + random.randint(-timing_variation, timing_variation)
        humanized_time = max(0, humanized_time)  # Ensure time is not negative
        
        # Add slight velocity variation
        humanized_velocity = velocity + random.randint(-velocity_variation, velocity_variation)
        humanized_velocity = max(1, min(127, humanized_velocity))  # Ensure valid velocity
        
        # Add slight duration variation (less than timing to avoid overlaps)
        humanized_duration = duration + random.randint(-timing_variation // 2, timing_variation // 2)
        humanized_duration = max(1, humanized_duration)  # Ensure duration is at least 1 tick
        
        humanized.append((note, humanized_velocity, humanized_time, humanized_duration))
    
    return humanized

def merge_tracks(tracks):
    """
    Merge multiple tracks into a single track.
    
    Args:
        tracks (list): List of lists of (note, velocity, time, duration) tuples
        
    Returns:
        list: Merged track
    """
    merged = []
    for track in tracks:
        merged.extend(track)
    
    # Sort by start time
    merged.sort(key=lambda x: x[2])
    
    return merged

def extract_melody_from_midi(midi_file, track_index=0, channel=None):
    """
    Extract a melody from a MIDI file.
    
    Args:
        midi_file (str): Path to MIDI file
        track_index (int): Index of the track to extract from
        channel (int): MIDI channel to extract from (None for all channels)
        
    Returns:
        list: Extracted melody as (note, velocity, time, duration) tuples
    """
    mid = mido.MidiFile(midi_file)
    
    if track_index >= len(mid.tracks):
        return []
    
    track = mid.tracks[track_index]
    
    # Extract notes
    notes = []
    current_time = 0
    active_notes = {}  # Dictionary to track active notes: {(note, channel): (start_time, velocity)}
    
    for msg in track:
        current_time += msg.time
        
        # Only process note messages for the specified channel (or all channels if None)
        if channel is not None and hasattr(msg, 'channel') and msg.channel != channel:
            continue
        
        if msg.type == 'note_on' and msg.velocity > 0:
            # Note started
            active_notes[(msg.note, msg.channel if hasattr(msg, 'channel') else 0)] = (current_time, msg.velocity)
        
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            # Note ended
            note_key = (msg.note, msg.channel if hasattr(msg, 'channel') else 0)
            if note_key in active_notes:
                start_time, velocity = active_notes[note_key]
                duration = current_time - start_time
                notes.append((msg.note, velocity, start_time, duration))
                del active_notes[note_key]
    
    # Sort by start time
    notes.sort(key=lambda x: x[2])
    
    return notes

def save_notes_to_midi(notes, output_file, tempo=120, channel=0):
    """
    Save a list of notes to a MIDI file.
    
    Args:
        notes (list): List of (note, velocity, time, duration) tuples
        output_file (str): Output filename
        tempo (int): Tempo in BPM
        channel (int): MIDI channel (0-15)
    """
    mid, track = create_midi_file(output_file, tempo)
    
    for note, velocity, time, duration in notes:
        add_note(track, note, velocity, time, duration, channel)
    
    mid.save(output_file)

def fix_note_timings(midi_file):
    """
    Fix note timings in a MIDI file to ensure proper playback.
    
    Args:
        midi_file (MidiFile): MIDI file object
        
    Returns:
        MidiFile: Fixed MIDI file
    """
    for track in midi_file.tracks:
        # Sort messages by absolute time
        messages = []
        absolute_time = 0
        
        for msg in track:
            absolute_time += msg.time
            messages.append((absolute_time, msg))
        
        # Sort messages
        messages.sort(key=lambda x: x[0])
        
        # Clear the track
        track.clear()
        
        # Recalculate delta times
        prev_time = 0
        for absolute_time, msg in messages:
            new_msg = msg.copy()
            new_msg.time = absolute_time - prev_time
            track.append(new_msg)
            prev_time = absolute_time
    
    return midi_file

def create_midi_file_from_notes(filename, notes_by_channel, tempo=120):
    """
    Create a MIDI file from notes organized by channel.
    
    Args:
        filename (str): Output filename
        notes_by_channel (dict): Dictionary mapping channel numbers to lists of (note, velocity, start_time, duration) tuples
        tempo (int): Tempo in BPM
        
    Returns:
        MidiFile: The created MIDI file
    """
    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = mid.add_track()
    
    # Set tempo
    tempo_us = mido.bpm2tempo(tempo)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo_us, time=0))
    
    # Collect all note on/off events
    events = []
    
    for channel, notes in notes_by_channel.items():
        for note, velocity, start_time, duration in notes:
            # Ensure values are integers
            note = int(note)
            velocity = int(velocity)
            start_time = int(start_time)
            duration = int(duration)
            
            # Limit duration to reasonable values (max 2 beats)
            max_duration = 2 * TICKS_PER_BEAT
            if duration > max_duration:
                duration = max_duration
            
            # Add note on event
            events.append(('note_on', note, velocity, start_time, channel))
            
            # Add note off event
            events.append(('note_off', note, 0, start_time + duration, channel))
    
    # Sort events by time
    events.sort(key=lambda x: x[3])
    
    # Convert to delta time
    last_time = 0
    for i, (msg_type, note, velocity, time, channel) in enumerate(events):
        delta_time = time - last_time
        last_time = time
        
        # Create and add the message
        if msg_type == 'note_on':
            track.append(mido.Message('note_on', note=note, velocity=velocity, time=delta_time, channel=channel))
        else:  # note_off
            track.append(mido.Message('note_off', note=note, velocity=velocity, time=delta_time, channel=channel))
    
    # Save the file
    mid.save(filename)
    
    return mid