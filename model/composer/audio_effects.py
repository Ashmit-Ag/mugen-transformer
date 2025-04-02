import mido
from .midi_utils import add_control_change

# MIDI CC numbers for common effects
REVERB_CC = 91
CHORUS_CC = 93
DELAY_CC = 94
FILTER_CUTOFF_CC = 74
FILTER_RESONANCE_CC = 71
DISTORTION_CC = 92  # Not standard but often used

def apply_reverb(track, amount, time=0, channel=0):
    """Apply reverb effect via MIDI CC."""
    value = int(min(1.0, max(0.0, amount)) * 127)
    add_control_change(track, REVERB_CC, value, time, channel)

def apply_chorus(track, amount, time=0, channel=0):
    """Apply chorus effect via MIDI CC."""
    value = int(min(1.0, max(0.0, amount)) * 127)
    add_control_change(track, CHORUS_CC, value, time, channel)

def apply_delay(track, amount, time=0, channel=0):
    """Apply delay/echo effect via MIDI CC."""
    value = int(min(1.0, max(0.0, amount)) * 127)
    add_control_change(track, DELAY_CC, value, time, channel)

def apply_filter(track, cutoff, resonance=0.5, time=0, channel=0):
    """Apply filter effect via MIDI CC."""
    cutoff_value = int(min(1.0, max(0.0, cutoff)) * 127)
    resonance_value = int(min(1.0, max(0.0, resonance)) * 127)
    
    add_control_change(track, FILTER_CUTOFF_CC, cutoff_value, time, channel)
    add_control_change(track, FILTER_RESONANCE_CC, resonance_value, time, channel)

def apply_distortion(track, amount, time=0, channel=0):
    """Apply distortion effect via MIDI CC."""
    value = int(min(1.0, max(0.0, amount)) * 127)
    add_control_change(track, DISTORTION_CC, value, time, channel)

def apply_effect_automation(track, effect_cc, start_value, end_value, duration_ticks, start_time=0, channel=0):
    """Create an automation curve for an effect parameter."""
    num_steps = 16  # Number of steps in the automation
    step_size = duration_ticks // num_steps
    
    for i in range(num_steps + 1):
        # Calculate the current value using linear interpolation
        t = i / num_steps
        current_value = int(start_value * (1 - t) + end_value * t)
        
        # Calculate the current time
        current_time = start_time + (i * step_size)
        
        # Add the control change
        add_control_change(track, effect_cc, current_value, current_time, channel)

def apply_filter_sweep(track, start_cutoff, end_cutoff, resonance, duration_ticks, start_time=0, channel=0):
    """Create a filter sweep automation."""
    # Convert values to MIDI range (0-127)
    start_value = int(min(1.0, max(0.0, start_cutoff)) * 127)
    end_value = int(min(1.0, max(0.0, end_cutoff)) * 127)
    resonance_value = int(min(1.0, max(0.0, resonance)) * 127)
    
    # Set resonance
    add_control_change(track, FILTER_RESONANCE_CC, resonance_value, start_time, channel)
    
    # Create cutoff automation
    apply_effect_automation(track, FILTER_CUTOFF_CC, start_value, end_value, duration_ticks, start_time, channel)