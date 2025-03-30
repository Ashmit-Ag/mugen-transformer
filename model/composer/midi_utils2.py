"""
MIDI utilities module for the procedural music generation system.
Provides functions for working with MIDI files and tracks.
"""

import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

# Constants
TICKS_PER_BEAT = 480  # Standard MIDI resolution

def create_midi_file(tempo=120, time_signature=(4, 4)):
    """
    Create a new MIDI file with multiple tracks for different instruments.
    
    Args:
        tempo (int): Tempo in BPM
        time_signature (tuple): Time signature as (numerator, denominator)
        
    Returns:
        tuple: (MidiFile, dict of tracks by channel)
    """
    mid = MidiFile(type=1)  # Type 1 supports multiple tracks
    
    # Create a tempo track (track 0)
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)
    
    # Add time signature
    tempo_track.append(MetaMessage('time_signature', numerator=time_signature[0], 
                                  denominator=time_signature[1], clocks_per_click=24, 
                                  notated_32nd_notes_per_beat=8, time=0))
    
    # Add tempo (microseconds per beat)
    tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo), time=0))
    
    # Create a dictionary to store tracks by channel
    tracks_by_channel = {}
    
    # Create tracks for each channel (0-15)
    for channel in range(16):
        track = MidiTrack()
        mid.tracks.append(track)
        tracks_by_channel[channel] = track
        
        # Add track name
        if channel == 9:
            track_name = f"Drums"
        else:
            track_name = f"Channel {channel}"
        
        track.append(MetaMessage('track_name', name=track_name, time=0))
    
    return mid, tracks_by_channel

def set_instrument(track, program, channel):
    """
    Set the instrument (program) for a track.
    
    Args:
        track (MidiTrack): MIDI track
        program (int): Program number (0-127)
        channel (int): MIDI channel (0-15)
    """
    track.append(Message('program_change', program=program, channel=channel, time=0))

def add_note(track, note, velocity, time, duration, channel):
    """
    Add a note to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        note (int): MIDI note number
        velocity (int): Note velocity (0-127)
        time (int): Start time in ticks
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    # Ensure note is within MIDI range
    if note < 0 or note > 127:
        return
    
    # Ensure velocity is within range
    velocity = max(1, min(127, velocity))
    
    # Add note_on message
    track.append(Message('note_on', note=note, velocity=velocity, channel=channel, time=time))
    
    # Add note_off message
    track.append(Message('note_off', note=note, velocity=0, channel=channel, time=time + duration))

def add_chord(track, notes, velocity, time, duration, channel):
    """
    Add a chord to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        notes (list): List of MIDI note numbers
        velocity (int): Note velocity (0-127)
        time (int): Start time in ticks
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    for note in notes:
        add_note(track, note, velocity, time, duration, channel)

def add_control_change(track, control, value, time, channel):
    """
    Add a control change message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        control (int): Control number
        value (int): Control value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    track.append(Message('control_change', control=control, value=value, channel=channel, time=time))

def apply_filter_sweep(track, start_value, end_value, duration_pct, total_duration, start_time, channel):
    """
    Apply a filter sweep effect.
    
    Args:
        track (MidiTrack): MIDI track
        start_value (int): Starting filter value (0-127)
        end_value (int): Ending filter value (0-127)
        duration_pct (int): Duration percentage (0-100)
        total_duration (int): Total duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Calculate actual duration
    duration = int(total_duration * duration_pct / 100)
    
    # Number of steps for the sweep
    num_steps = 16
    
    # Calculate step size
    step_size = (end_value - start_value) / num_steps
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the sweep
    for i in range(num_steps + 1):
        value = int(start_value + step_size * i)
        value = max(0, min(127, value))
        time = start_time + (i * time_step)
        
        # Add control change for filter cutoff
        add_control_change(track, 74, value, time, channel)

def apply_effect_automation(track, cc_number, start_value, end_value, duration, start_time, channel):
    """
    Apply automation to an effect parameter.
    
    Args:
        track (MidiTrack): MIDI track
        cc_number (int): Control change number
        start_value (int): Starting value (0-127)
        end_value (int): Ending value (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the automation
    num_steps = 8
    
    # Calculate step size
    step_size = (end_value - start_value) / num_steps
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the automation
    for i in range(num_steps + 1):
        value = int(start_value + step_size * i)
        value = max(0, min(127, value))
        time = start_time + (i * time_step)
        
        # Add control change
        add_control_change(track, cc_number, value, time, channel)

def add_sustain_pedal(track, start_time, duration, channel):
    """
    Add sustain pedal to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        start_time (int): Start time in ticks
        duration (int): Duration in ticks
        channel (int): MIDI channel (0-15)
    """
    # Sustain pedal on
    add_control_change(track, 64, 127, start_time, channel)
    
    # Sustain pedal off
    add_control_change(track, 64, 0, start_time + duration, channel)

def add_pitch_bend(track, value, time, channel):
    """
    Add a pitch bend message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Pitch bend value (-8192 to 8191)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Convert to MIDI pitch bend range (0-16383, with 8192 as center)
    midi_value = value + 8192
    midi_value = max(0, min(16383, midi_value))
    
    # Extract MSB and LSB
    msb = (midi_value >> 7) & 0x7F
    lsb = midi_value & 0x7F
    
    track.append(Message('pitchwheel', pitch=value, channel=channel, time=time))

def add_aftertouch(track, note, value, time, channel):
    """
    Add an aftertouch (polyphonic key pressure) message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        note (int): MIDI note number
        value (int): Pressure value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    track.append(Message('polytouch', note=note, value=value, channel=channel, time=time))

def add_channel_pressure(track, value, time, channel):
    """
    Add a channel pressure (monophonic aftertouch) message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Pressure value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    track.append(Message('aftertouch', value=value, channel=channel, time=time))

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

def add_pan(track, value, time, channel):
    """
    Add a pan controller message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Pan value (0-127, 64 is center)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 10, value, time, channel)

def add_volume(track, value, time, channel):
    """
    Add a volume controller message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Volume value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 7, value, time, channel)

def add_reverb(track, value, time, channel):
    """
    Add a reverb controller message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Reverb value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 91, value, time, channel)

def add_chorus(track, value, time, channel):
    """
    Add a chorus controller message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Chorus value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 93, value, time, channel)

def add_portamento(track, value, time, channel):
    """
    Add a portamento controller message to a MIDI track.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Portamento value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, 5, value, time, channel)

def sort_midi_file(midi_file):
    """
    Sort all events in a MIDI file by time.
    
    Args:
        midi_file (MidiFile): MIDI file to sort
        
    Returns:
        MidiFile: Sorted MIDI file
    """
    for track in midi_file.tracks:
        # Convert track to a list of (time, message) tuples
        events = []
        current_time = 0
        
        for msg in track:
            current_time += msg.time
            events.append((current_time, msg))
        
        # Sort events by time
        events.sort(key=lambda x: x[0])
        
        # Clear the track
        track.clear()
        
        # Add sorted events back to the track
        prev_time = 0
        for time, msg in events:
            # Calculate delta time
            delta_time = time - prev_time
            msg.time = delta_time
            track.append(msg)
            prev_time = time
    
    return midi_file

def save_midi_file(midi_file, filename):
    """
    Save a MIDI file.
    
    Args:
        midi_file (MidiFile): MIDI file to save
        filename (str): Output filename
    """
    # Sort the MIDI file before saving
    sorted_midi = sort_midi_file(midi_file)
    sorted_midi.save(filename)