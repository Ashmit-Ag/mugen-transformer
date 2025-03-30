"""
Audio effects module for the procedural music generation system.
Provides functions for applying audio effects to MIDI tracks.
"""

from .midi_utils import add_control_change, add_pitch_bend, add_modulation, add_expression
import random

# MIDI CC numbers for common effects
REVERB_CC = 91
CHORUS_CC = 93
DELAY_CC = 94
FILTER_CUTOFF_CC = 74
FILTER_RESONANCE_CC = 71
DISTORTION_CC = 92
RELEASE_CC = 72
ATTACK_CC = 73
BRIGHTNESS_CC = 74
PORTAMENTO_CC = 5
SUSTAIN_CC = 64
EXPRESSION_CC = 11
MODULATION_CC = 1
PAN_CC = 10
VOLUME_CC = 7

def apply_reverb(track, value, time, channel):
    """
    Apply reverb effect.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Reverb value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, REVERB_CC, value, time, channel)

def apply_chorus(track, value, time, channel):
    """
    Apply chorus effect.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Chorus value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, CHORUS_CC, value, time, channel)

def apply_delay(track, value, time, channel):
    """
    Apply delay effect.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Delay value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, DELAY_CC, value, time, channel)

def apply_filter(track, cutoff, resonance, time, channel):
    """
    Apply filter effect.
    
    Args:
        track (MidiTrack): MIDI track
        cutoff (int): Filter cutoff value (0-127)
        resonance (int): Filter resonance value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, FILTER_CUTOFF_CC, cutoff, time, channel)
    add_control_change(track, FILTER_RESONANCE_CC, resonance, time, channel)

def apply_distortion(track, value, time, channel):
    """
    Apply distortion effect.
    
    Args:
        track (MidiTrack): MIDI track
        value (int): Distortion value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, DISTORTION_CC, value, time, channel)

def apply_envelope(track, attack, release, time, channel):
    """
    Apply envelope effect.
    
    Args:
        track (MidiTrack): MIDI track
        attack (int): Attack value (0-127)
        release (int): Release value (0-127)
        time (int): Time in ticks
        channel (int): MIDI channel (0-15)
    """
    add_control_change(track, ATTACK_CC, attack, time, channel)
    add_control_change(track, RELEASE_CC, release, time, channel)

def apply_vibrato(track, depth, rate, duration, start_time, channel):
    """
    Apply vibrato effect.
    
    Args:
        track (MidiTrack): MIDI track
        depth (int): Vibrato depth (0-127)
        rate (int): Vibrato rate (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the vibrato
    num_steps = 16
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the vibrato
    for i in range(num_steps + 1):
        # Calculate modulation value using sine wave
        value = depth * (0.5 + 0.5 * (i % 2))  # Simple alternating pattern
        value = max(0, min(127, int(value)))
        time = start_time + (i * time_step)
        
        # Add modulation
        add_modulation(track, value, time, channel)

def apply_tremolo(track, depth, rate, duration, start_time, channel):
    """
    Apply tremolo effect.
    
    Args:
        track (MidiTrack): MIDI track
        depth (int): Tremolo depth (0-127)
        rate (int): Tremolo rate (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the tremolo
    num_steps = 16
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Base expression value
    base_expression = 100
    
    # Apply the tremolo
    for i in range(num_steps + 1):
        # Calculate expression value using sine wave
        value = base_expression - depth * (0.5 + 0.5 * (i % 2))  # Simple alternating pattern
        value = max(0, min(127, int(value)))
        time = start_time + (i * time_step)
        
        # Add expression
        add_expression(track, value, time, channel)

def apply_filter_sweep(track, start_cutoff, end_cutoff, resonance, duration, start_time, channel):
    """
    Apply filter sweep effect.
    
    Args:
        track (MidiTrack): MIDI track
        start_cutoff (int): Starting cutoff value (0-127)
        end_cutoff (int): Ending cutoff value (0-127)
        resonance (int): Resonance value (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the sweep
    num_steps = 16
    
    # Calculate step size
    step_size = (end_cutoff - start_cutoff) / num_steps
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the sweep
    for i in range(num_steps + 1):
        value = int(start_cutoff + step_size * i)
        value = max(0, min(127, value))
        time = start_time + (i * time_step)
        
        # Add filter cutoff
        add_control_change(track, FILTER_CUTOFF_CC, value, time, channel)
        
        # Add filter resonance
        add_control_change(track, FILTER_RESONANCE_CC, resonance, time, channel)

def apply_pitch_bend_sweep(track, start_bend, end_bend, duration, start_time, channel):
    """
    Apply pitch bend sweep effect.
    
    Args:
        track (MidiTrack): MIDI track
        start_bend (int): Starting pitch bend value (-8192 to 8191)
        end_bend (int): Ending pitch bend value (-8192 to 8191)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the sweep
    num_steps = 16
    
    # Calculate step size
    step_size = (end_bend - start_bend) / num_steps
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the sweep
    for i in range(num_steps + 1):
        value = int(start_bend + step_size * i)
        value = max(-8192, min(8191, value))
        time = start_time + (i * time_step)
        
        # Add pitch bend
        add_pitch_bend(track, value, time, channel)

def apply_volume_fade(track, start_volume, end_volume, duration, start_time, channel):
    """
    Apply volume fade effect.
    
    Args:
        track (MidiTrack): MIDI track
        start_volume (int): Starting volume value (0-127)
        end_volume (int): Ending volume value (0-127)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the fade
    num_steps = 16
    
    # Calculate step size
    step_size = (end_volume - start_volume) / num_steps
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the fade
    for i in range(num_steps + 1):
        value = int(start_volume + step_size * i)
        value = max(0, min(127, value))
        time = start_time + (i * time_step)
        
        # Add volume
        add_control_change(track, VOLUME_CC, value, time, channel)

def apply_pan_sweep(track, start_pan, end_pan, duration, start_time, channel):
    """
    Apply pan sweep effect.
    
    Args:
        track (MidiTrack): MIDI track
        start_pan (int): Starting pan value (0-127, 64 is center)
        end_pan (int): Ending pan value (0-127, 64 is center)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Number of steps for the sweep
    num_steps = 16
    
    # Calculate step size
    step_size = (end_pan - start_pan) / num_steps
    
    # Calculate time between steps
    time_step = duration // num_steps
    
    # Apply the sweep
    for i in range(num_steps + 1):
        value = int(start_pan + step_size * i)
        value = max(0, min(127, value))
        time = start_time + (i * time_step)
        
        # Add pan
        add_control_change(track, PAN_CC, value, time, channel)

def apply_random_effects(track, intensity, duration, start_time, channel):
    """
    Apply random effects based on intensity.
    
    Args:
        track (MidiTrack): MIDI track
        intensity (float): Intensity of effects (0.0 to 1.0)
        duration (int): Duration in ticks
        start_time (int): Start time in ticks
        channel (int): MIDI channel (0-15)
    """
    # Apply effects based on intensity
    if random.random() < intensity * 0.7:
        # Apply reverb
        reverb_value = int(40 + intensity * 60)
        apply_reverb(track, reverb_value, start_time, channel)
    
    if random.random() < intensity * 0.5:
        # Apply chorus
        chorus_value = int(30 + intensity * 50)
        apply_chorus(track, chorus_value, start_time, channel)
    
    if random.random() < intensity * 0.3:
        # Apply delay
        delay_value = int(20 + intensity * 40)
        apply_delay(track, delay_value, start_time, channel)
    
    if random.random() < intensity * 0.4:
        # Apply filter
        cutoff_value = int(60 + intensity * 40)
        resonance_value = int(40 + intensity * 40)
        apply_filter(track, cutoff_value, resonance_value, start_time, channel)
    
    if random.random() < intensity * 0.2:
        # Apply distortion
        distortion_value = int(20 + intensity * 40)
        apply_distortion(track, distortion_value, start_time, channel)
    
    if random.random() < intensity * 0.6:
        # Apply envelope
        attack_value = int(10 + intensity * 30)
        release_value = int(40 + intensity * 60)
        apply_envelope(track, attack_value, release_value, start_time, channel)
    
    if random.random() < intensity * 0.3:
        # Apply vibrato
        depth_value = int(20 + intensity * 40)
        rate_value = int(40 + intensity * 40)
        apply_vibrato(track, depth_value, rate_value, duration, start_time, channel)
    
    if random.random() < intensity * 0.3:
        # Apply tremolo
        depth_value = int(10 + intensity * 30)
        rate_value = int(40 + intensity * 40)
        apply_tremolo(track, depth_value, rate_value, duration, start_time, channel)
    
    if random.random() < intensity * 0.2:
        # Apply filter sweep
        start_cutoff = int(40 + intensity * 40)
        end_cutoff = int(80 + intensity * 40)
        resonance_value = int(40 + intensity * 40)
        apply_filter_sweep(track, start_cutoff, end_cutoff, resonance_value, duration, start_time, channel)
    
    if random.random() < intensity * 0.1:
        # Apply pitch bend sweep
        start_bend = int(-2000 * intensity)
        end_bend = int(2000 * intensity)
        apply_pitch_bend_sweep(track, start_bend, end_bend, duration, start_time, channel)
    
    if random.random() < intensity * 0.4:
        # Apply volume fade
        start_volume = int(80 - intensity * 20)
        end_volume = int(80 + intensity * 20)
        apply_volume_fade(track, start_volume, end_volume, duration, start_time, channel)
    
    if random.random() < intensity * 0.3:
        # Apply pan sweep
        start_pan = int(64 - intensity * 30)
        end_pan = int(64 + intensity * 30)
        apply_pan_sweep(track, start_pan, end_pan, duration, start_time, channel)