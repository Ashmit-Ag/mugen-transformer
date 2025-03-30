"""
MIDI utilities module for the procedural music generation system.
Provides functions for working with MIDI files and messages.
"""

import mido
import random

# Define constants
TICKS_PER_BEAT = 480  # Standard MIDI resolution

def create_midi_file(tempo=120, time_signature=(4, 4)):
    """
    Create a new MIDI file.
    
    Args:
        tempo (int): Tempo in BPM
        time_signature (tuple): Time signature as (numerator, denominator)
        
    Returns:
        MidiFile: MIDI file object
    """
    # Create a new MIDI file
    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    
    # Create a track for metadata
    meta_track = mido.MidiTrack()
    mid.tracks.append(meta_track)
    
    # Add tempo message
    tempo_in_microseconds = mido.bpm2tempo(tempo)
    meta_track.append(mido.MetaMessage('set_tempo', tempo=tempo_in_microseconds, time=0))
    
    # Add time signature message
    numerator, denominator = time_signature
    meta_track.append(mido.MetaMessage('time_signature', numerator=numerator, denominator=denominator, time=0))
    
    return mid

def create_tracks_by_channel(midi_file, num_channels=16):
    """
    Create separate tracks for each MIDI channel.
    
    Args:
        midi_file (MidiFile): MIDI file object
        num_channels (int): Number of channels to create tracks for
        
    Returns:
        dict: Dictionary of tracks by channel number
    """
    tracks_by_channel = {}
    
    # Create a track for each channel
    for channel in range(num_channels):
        track = mido.MidiTrack()
        track.name = f"Channel {channel}"
        midi_file.tracks.append(track)
        tracks_by_channel[channel] = track
    
    return tracks_by_channel

def add_program_change(track, program, channel):
    """
    Add a program change message to a track.
    
    Args:
        track (MidiTrack): MIDI track
        program (int): Program number (0-127)
        channel (int): MIDI channel (0-15)
    """
    track.append(mido.Message('program_change', program=program, channel=channel, time=0))

def add_note(track, note, velocity, time, duration, channel):
    """
    Add a note to a track.
    
    Args:
        track (MidiTrack): MIDI track
        note (int): MIDI note number
        velocity (int): Note velocity (0-127)
        time (int): Start time in ticks (absolute)
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    # Skip rest notes (represented by note=-1)
    if note < 0:
        return
    
    # Ensure note is within MIDI range
    if note < 0 or note > 127:
        return
    
    # Sort the track by absolute time to ensure proper delta time calculation
    events = []
    
    # Extract existing events with their absolute times
    absolute_time = 0
    for msg in track:
        absolute_time += msg.time
        events.append((absolute_time, msg))
    
    # Add new note_on and note_off events
    events.append((time, mido.Message('note_on', note=note, velocity=velocity, channel=channel, time=0)))
    events.append((time + duration, mido.Message('note_off', note=note, velocity=0, channel=channel, time=0)))
    
    # Sort events by absolute time
    events.sort(key=lambda x: x[0])
    
    # Clear the track
    track.clear()
    
    # Recalculate delta times and add messages back to the track
    prev_time = 0
    for absolute_time, msg in events:
        delta_time = absolute_time - prev_time
        msg.time = delta_time
        track.append(msg)
        prev_time = absolute_time

def add_chord(track, notes, velocity, time, duration, channel):
    """
    Add a chord to a track.
    
    Args:
        track (MidiTrack): MIDI track
        notes (list): List of MIDI note numbers
        velocity (int): Note velocity (0-127)
        time (int): Start time in ticks (absolute)
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    for note in notes:
        add_note(track, note, velocity, time, duration, channel)

def add_control_change(track, control, value, time, channel):
    """
    Add a control change message to a track.
    
    Args:
        track (MidiTrack): MIDI track
        control (int): Control number (0-127)
        value (int): Control value (0-127)
        time (int): Time in ticks (absolute)
        channel (int): MIDI channel (0-15)
    """
    # Sort the track by absolute time to ensure proper delta time calculation
    events = []
    
    # Extract existing events with their absolute times
    absolute_time = 0
    for msg in track:
        absolute_time += msg.time
        events.append((absolute_time, msg))
    
    # Add new control change event
    events.append((time, mido.Message('control_change', control=control, value=value, channel=channel, time=0)))
    
    # Sort events by absolute time
    events.sort(key=lambda x: x[0])
    
    # Clear the track
    track.clear()
    
    # Recalculate delta times and add messages back to the track
    prev_time = 0
    for absolute_time, msg in events:
        delta_time = absolute_time - prev_time
        msg.time = delta_time
        track.append(msg)
        prev_time = absolute_time

def add_pitch_bend(track, value, time, channel):
    """
    Add a pitch bend message to a track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Pitch bend value (-8192 to 8191)
        time (int): Time in ticks (absolute)
        channel (int): MIDI channel (0-15)
    """
    # Sort the track by absolute time to ensure proper delta time calculation
    events = []
    
    # Extract existing events with their absolute times
    absolute_time = 0
    for msg in track:
        absolute_time += msg.time
        events.append((absolute_time, msg))
    
    # Add new pitch bend event
    events.append((time, mido.Message('pitchwheel', pitch=value, channel=channel, time=0)))
    
    # Sort events by absolute time
    events.sort(key=lambda x: x[0])
    
    # Clear the track
    track.clear()
    
    # Recalculate delta times and add messages back to the track
    prev_time = 0
    for absolute_time, msg in events:
        delta_time = absolute_time - prev_time
        msg.time = delta_time
        track.append(msg)
        prev_time = absolute_time

def add_sustain_pedal(track, time, duration, channel):
    """
    Add sustain pedal messages to a track.
    
    Args:
        track (MidiTrack): MIDI track
        time (int): Start time in ticks (absolute)
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    # Add sustain pedal on
    add_control_change(track, 64, 127, time, channel)
    
    # Add sustain pedal off
    add_control_change(track, 64, 0, time + duration, channel)

def apply_filter_sweep(track, start_value, end_value, duration, time, channel):
    """
    Apply a filter sweep to a track.
    
    Args:
        track (MidiTrack): MIDI track
        start_value (int): Starting filter value (0-127)
        end_value (int): Ending filter value (0-127)
        duration (int): Duration in ticks
        time (int): Start time in ticks (absolute)
        channel (int): MIDI channel (0-15)
    """
    # Number of steps in the sweep
    num_steps = 16
    
    # Calculate step size
    step_size = (end_value - start_value) / num_steps
    
    # Calculate time step
    time_step = duration / num_steps
    
    # Add filter cutoff messages
    for i in range(num_steps + 1):
        value = int(start_value + step_size * i)
        value = max(0, min(127, value))  # Ensure value is within MIDI range
        
        # Add filter cutoff message
        add_control_change(track, 74, value, time + int(time_step * i), channel)

def apply_effect_automation(track, control, start_value, end_value, duration, time, channel):
    """
    Apply effect automation to a track.
    
    Args:
        track (MidiTrack): MIDI track
        control (int): Control number (0-127)
        start_value (int): Starting value (0-127)
        end_value (int): Ending value (0-127)
        duration (int): Duration in ticks
        time (int): Start time in ticks (absolute)
        channel (int): MIDI channel (0-15)
    """
    # Number of steps in the automation
    num_steps = 8
    
    # Calculate step size
    step_size = (end_value - start_value) / num_steps
    
    # Calculate time step
    time_step = duration / num_steps
    
    # Add control change messages
    for i in range(num_steps + 1):
        value = int(start_value + step_size * i)
        value = max(0, min(127, value))  # Ensure value is within MIDI range
        
        # Add control change message
        add_control_change(track, control, value, time + int(time_step * i), channel)

def add_modulation(track, value, time, channel):
    """
    Add a modulation wheel message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Modulation value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 1, value, time, channel)

def add_expression(track, value, time, channel):
    """
    Add an expression controller message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Expression value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 11, value, time, channel)


def add_random_variation(value, amount=5):
    """
    Add random variation to a value.
    
    Args:
        value (int): Base value
        amount (int): Maximum amount of variation
        
    Returns:
        int: Value with random variation
    """
    return max(0, min(127, value + random.randint(-amount, amount)))

def quantize_time(time, grid_size):
    """
    Quantize a time value to a grid.
    
    Args:
        time (int): Time in ticks
        grid_size (int): Grid size in ticks
        
    Returns:
        int: Quantized time
    """
    return (time // grid_size) * grid_size

def humanize_time(time, amount=10):
    """
    Add humanization to a time value.
    
    Args:
        time (int): Time in ticks
        amount (int): Maximum amount of humanization
        
    Returns:
        int: Humanized time
    """
    return time + random.randint(-amount, amount)

def humanize_velocity(velocity, amount=10):
    """
    Add humanization to a velocity value.
    
    Args:
        velocity (int): Velocity value
        amount (int): Maximum amount of humanization
        
    Returns:
        int: Humanized velocity
    """
    return max(1, min(127, velocity + random.randint(-amount, amount)))

def save_midi_file(midi_file, filename):
    """
    Save a MIDI file.
    
    Args:
        midi_file (MidiFile): MIDI file object
        filename (str): Output filename
    """
    midi_file.save(filename)

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