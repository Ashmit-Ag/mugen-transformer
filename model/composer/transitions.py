"""
Transitions module for the procedural music generation system.
Provides functions for creating transitions between song sections.
"""

import random
from .midi_utils import add_note, add_control_change, apply_filter_sweep, apply_effect_automation

# Channel assignments
DRUM_CHANNEL = 9
BASS_CHANNEL = 0
CHORD_CHANNEL = 1
MELODY_CHANNEL = 2
BG_MELODY_CHANNEL = 3
SECONDARY_MELODY_CHANNEL = 4
SECONDARY_BG_MELODY_CHANNEL = 5
SECONDARY_BASS_CHANNEL = 6
SECONDARY_DRUM_CHANNEL = 10

# MIDI CC numbers for common effects
REVERB_CC = 91
CHORUS_CC = 93
DELAY_CC = 94
FILTER_CUTOFF_CC = 74
FILTER_RESONANCE_CC = 71
DISTORTION_CC = 92

# MIDI note numbers for drum sounds
KICK = 36
SNARE = 38
CLAP = 39
CLOSED_HAT = 42
PEDAL_HAT = 44
OPEN_HAT = 46
LOW_TOM = 41
MID_TOM = 47
HIGH_TOM = 50
CRASH = 49
RIDE = 51
TAMBOURINE = 54

class TransitionGenerator:
    """Class for generating transitions between song sections."""
    
    def __init__(self, scale, ticks_per_beat=480):
        """
        Initialize the transition generator.
        
        Args:
            scale (list): List of scale notes
            ticks_per_beat (int): Number of ticks per beat
        """
        self.scale = scale
        self.ticks_per_beat = ticks_per_beat
    
    def generate_riser(self, duration_ticks, intensity=0.8):
        """
        Generate a riser transition.
        
        Args:
            duration_ticks (int): Duration of the riser in ticks
            intensity (float): Intensity of the riser (0.0 to 1.0)
            
        Returns:
            list: List of (note, velocity, time, duration) tuples
        """
        riser_notes = []
        
        # Number of notes in the riser
        num_notes = int(4 + intensity * 12)
        
        # Duration of each note
        note_duration = duration_ticks // num_notes
        
        # Starting note (low in the scale)
        start_note = self.scale[0] - 12
        
        # Generate ascending notes
        for i in range(num_notes):
            # Calculate the note (ascending through the scale)
            note_index = i % len(self.scale)
            octave = i // len(self.scale)
            note = self.scale[note_index] + (octave * 12)
            
            # Ensure the note is within MIDI range
            if note < 0 or note > 127:
                continue
            
            # Calculate time
            time = i * note_duration
            
            # Calculate velocity (crescendo)
            velocity = 60 + int((i / num_notes) * 67)
            
            # Add the note
            riser_notes.append((note, velocity, time, note_duration))
        
        return riser_notes
    
    def generate_reverse_cymbal(self, duration_ticks):
        """
        Generate a reverse cymbal effect.
        
        Args:
            duration_ticks (int): Duration of the effect in ticks
            
        Returns:
            list: List of (note, velocity, time, duration) tuples
        """
        # Reverse cymbal is typically a single note with increasing velocity
        cymbal_note = CRASH  # Crash cymbal
        
        # Create a series of notes with increasing velocity
        cymbal_notes = []
        steps = 8
        
        for i in range(steps):
            time = i * (duration_ticks // steps)
            velocity = 40 + int((i / steps) * 87)  # Crescendo from 40 to 127
            duration = duration_ticks // steps
            
            cymbal_notes.append((cymbal_note, velocity, time, duration))
        
        return cymbal_notes
    
    def generate_drum_fill(self, duration_ticks, intensity=0.8):
        """
        Generate a drum fill.
        
        Args:
            duration_ticks (int): Duration of the fill in ticks
            intensity (float): Intensity of the fill (0.0 to 1.0)
            
        Returns:
            list: List of (note, velocity, time, duration) tuples
        """
        fill_notes = []
        
        # Use sixteenth notes for the fill
        grid_resolution = self.ticks_per_beat // 4
        
        # Number of grid positions
        grid_positions = duration_ticks // grid_resolution
        
        # Create a build-up pattern
        for i in range(grid_positions):
            # Determine if we should place a note at this position
            # Higher probability towards the end for a build-up effect
            probability = 0.3 + (i / grid_positions) * intensity * 0.7
            
            if random.random() < probability:
                time = i * grid_resolution
                
                # Choose a drum sound based on position
                if i == grid_positions - 1:
                    # Last position gets a crash
                    note = CRASH
                    velocity = 127
                elif i % 4 == 0:
                    # Downbeats get kicks or snares
                    note = random.choice([KICK, SNARE])
                    velocity = random.randint(100, 127)
                elif i % 2 == 0:
                    # Even positions get hi-hats or snares
                    note = random.choice([CLOSED_HAT, SNARE])
                    velocity = random.randint(80, 110)
                else:
                    # Odd positions get hi-hats or toms
                    note = random.choice([CLOSED_HAT, LOW_TOM, MID_TOM, HIGH_TOM])
                    velocity = random.randint(70, 100)
                
                # Add crescendo effect
                velocity = min(127, int(velocity * (0.7 + (i / grid_positions) * 0.3)))
                
                # Fixed duration to ensure consistent timing
                duration = min(grid_resolution, self.ticks_per_beat // 4)
                
                fill_notes.append((note, velocity, time, duration))
        
        return fill_notes
    
    def generate_impact(self, time):
        """
        Generate an impact sound.
        
        Args:
            time (int): Time of the impact in ticks
            
        Returns:
            list: List of (note, velocity, time, duration) tuples
        """
        impact_notes = []
        
        # Impact is typically a kick and crash together
        kick = KICK
        crash = CRASH
        
        # Add the kick
        impact_notes.append((kick, 127, time, self.ticks_per_beat // 2))
        
        # Add the crash
        impact_notes.append((crash, 127, time, self.ticks_per_beat))
        
        return impact_notes
    
    def generate_beat_drop(self, duration_ticks):
        """
        Generate a beat drop effect.
        
        Args:
            duration_ticks (int): Duration of the effect in ticks
            
        Returns:
            list: List of (note, velocity, time, duration) tuples
        """
        drop_notes = []
        
        # Beat drop typically has a strong kick pattern
        kick = KICK
        snare = SNARE
        closed_hat = CLOSED_HAT
        
        # Duration of one beat
        beat_duration = self.ticks_per_beat
        
        # Number of beats in the drop
        num_beats = duration_ticks // beat_duration
        
        # Generate the drop pattern
        for i in range(num_beats):
            # Add a kick on every beat
            drop_notes.append((kick, 127, i * beat_duration, beat_duration // 4))
            
            # Add a snare on beats 2 and 4
            if i % 2 == 1:
                drop_notes.append((snare, 110, i * beat_duration, beat_duration // 4))
            
            # Add hi-hats on eighth notes
            for j in range(2):
                drop_notes.append((closed_hat, 90, i * beat_duration + j * (beat_duration // 2), beat_duration // 4))
        
        return drop_notes

def generate_ending_transition(scale, duration_ticks, intensity=0.7):
    """
    Generate an ending transition.
    
    Args:
        scale (list): List of scale notes
        duration_ticks (int): Duration of the transition in ticks
        intensity (float): Intensity of the transition (0.0 to 1.0)
        
    Returns:
        list: List of (note, velocity, time, duration, channel) tuples
    """
    transition_notes = []
    
    # Create a transition generator
    transition_gen = TransitionGenerator(scale)
    
    # Add a drum fill
    drum_fill = transition_gen.generate_drum_fill(duration_ticks, intensity)
    for note, velocity, time, duration in drum_fill:
        transition_notes.append((note, velocity, time, duration, DRUM_CHANNEL))
    
    # Add a final chord
    root_note = scale[0]
    chord_notes = [root_note, root_note + 4, root_note + 7]  # Major chord
    
    for note in chord_notes:
        if 0 <= note <= 127:
            transition_notes.append((note, 100, 0, duration_ticks, CHORD_CHANNEL))
    
    # Add a final bass note
    transition_notes.append((root_note - 12, 110, 0, duration_ticks, BASS_CHANNEL))
    
    return transition_notes

def apply_transition(track, from_intensity, to_intensity, start_time, ticks_per_bar, style, scale):
    """
    Apply a transition between two sections.
    
    Args:
        track (MidiTrack): MIDI track to apply the transition to
        from_intensity (float): Intensity of the source section (0.0 to 1.0)
        to_intensity (float): Intensity of the target section (0.0 to 1.0)
        start_time (int): Start time of the transition in ticks
        ticks_per_bar (int): Number of ticks per bar
        style (str): Music style
        scale (list): List of scale notes
    """
    # Create a transition generator
    transition_gen = TransitionGenerator(scale)
    
    # Determine transition type based on intensity change
    intensity_change = to_intensity - from_intensity
    
    # Duration of the transition (half a bar)
    transition_duration = ticks_per_bar // 2
    
    if intensity_change > 0.3:
        # Significant increase in intensity - use a riser and drum fill
        riser_notes = transition_gen.generate_riser(transition_duration, min(1.0, from_intensity + 0.3))
        for note, velocity, time, duration in riser_notes:
            add_note(track, note, velocity, start_time + time, duration, SECONDARY_MELODY_CHANNEL)
        
        # Add a proper drum fill
        drum_fill = transition_gen.generate_drum_fill(transition_duration, min(1.0, to_intensity))
        for note, velocity, time, duration in drum_fill:
            add_note(track, note, velocity, start_time + time, duration, DRUM_CHANNEL)
        
        # Add filter sweep
        apply_filter_sweep(track, 40, 127, 100, transition_duration, start_time, MELODY_CHANNEL)
        
        # If transitioning to a high-intensity section, add a beat drop
        if to_intensity > 0.8:
            beat_drop = transition_gen.generate_beat_drop(transition_duration // 2)
            for note, velocity, time, duration in beat_drop:
                add_note(track, note, velocity, start_time + transition_duration // 2 + time, duration, DRUM_CHANNEL)
        
    elif intensity_change < -0.3:
        # Significant decrease in intensity - use a reverse cymbal
        cymbal_notes = transition_gen.generate_reverse_cymbal(transition_duration)
        for note, velocity, time, duration in cymbal_notes:
            add_note(track, note, velocity, start_time + time, duration, DRUM_CHANNEL)
        
        # Add filter sweep
        apply_filter_sweep(track, 127, 40, 80, transition_duration, start_time, MELODY_CHANNEL)
        
    else:
        # Moderate change - use a simple drum fill
        drum_fill = transition_gen.generate_drum_fill(transition_duration, (from_intensity + to_intensity) / 2)
        for note, velocity, time, duration in drum_fill:
            add_note(track, note, velocity, start_time + time, duration, DRUM_CHANNEL)
    
    # Apply effect automation based on intensity change
    if abs(intensity_change) > 0.2:
        # Automate reverb
        start_reverb = int(from_intensity * 80)
        end_reverb = int(to_intensity * 80)
        apply_effect_automation(track, REVERB_CC, start_reverb, end_reverb, transition_duration, start_time, MELODY_CHANNEL)
        
        # Automate delay for atmospheric transitions
        if style == 'ambient' or from_intensity < 0.4 or to_intensity < 0.4:
            start_delay = int(from_intensity * 60)
            end_delay = int(to_intensity * 60)
            apply_effect_automation(track, DELAY_CC, start_delay, end_delay, transition_duration, start_time, MELODY_CHANNEL)

def apply_ending_transition(track, final_intensity, start_time, ticks_per_bar, style, scale):
    """
    Apply an ending transition to a song.
    
    Args:
        track (MidiTrack): MIDI track to apply the transition to
        final_intensity (float): Intensity of the final section (0.0 to 1.0)
        start_time (int): Start time of the transition in ticks
        ticks_per_bar (int): Number of ticks per bar
        style (str): Music style
        scale (list): List of scale notes
    """
    # Duration of the ending transition (1 bar)
    transition_duration = ticks_per_bar
    
    # Generate ending transition notes
    ending_notes = generate_ending_transition(scale, transition_duration, final_intensity)
    
    # Add the notes to the track
    for note, velocity, time, duration, channel in ending_notes:
        add_note(track, note, velocity, start_time + time, duration, channel)
    
    # Apply effect automation for ending
    if style == 'ambient' or final_intensity < 0.5:
        # Fade out with reverb
        apply_effect_automation(track, REVERB_CC, int(final_intensity * 80), 127, transition_duration, start_time, MELODY_CHANNEL)
        apply_effect_automation(track, DELAY_CC, int(final_intensity * 60), 100, transition_duration, start_time, MELODY_CHANNEL)
    else:
        # More dramatic ending for high-intensity songs
        # Filter sweep down
        apply_filter_sweep(track, 127, 20, 100, transition_duration, start_time, MELODY_CHANNEL)
        
        # Add impact at the very end
        transition_gen = TransitionGenerator(scale)
        impact_notes = transition_gen.generate_impact(start_time + transition_duration - 10)
        for note, velocity, time, duration in impact_notes:
            add_note(track, note, velocity, time, duration, DRUM_CHANNEL)