"""
Rhythm generator module for the procedural music generation system.
Provides functions for creating drum patterns and rhythmic elements.
"""

import random
from .midi_utils import TICKS_PER_BEAT

# MIDI note numbers for drum sounds
KICK = 36
SNARE = 38
CLAP = 39
RIM = 37
CLOSED_HAT = 42
PEDAL_HAT = 44
OPEN_HAT = 46
LOW_TOM = 41
MID_TOM = 47
HIGH_TOM = 50
CRASH = 49
RIDE = 51
TAMBOURINE = 54

def generate_drum_pattern(num_bars, beats_per_bar, complexity=0.5, is_phonk=False):
    """
    Generate a drum pattern.
    
    Args:
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the pattern (0.0 to 1.0)
        is_phonk (bool): Whether to use phonk-style drums
        
    Returns:
        list: Drum pattern as (note, velocity, time, duration) tuples
    """
    pattern = []
    
    # Calculate total ticks
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    total_ticks = num_bars * ticks_per_bar
    
    # Determine the grid resolution based on complexity
    if complexity < 0.3:
        # Quarter notes
        grid_resolution = TICKS_PER_BEAT
    elif complexity < 0.6:
        # Eighth notes
        grid_resolution = TICKS_PER_BEAT // 2
    else:
        # Sixteenth notes
        grid_resolution = TICKS_PER_BEAT // 4
    
    # Number of grid positions
    grid_positions = total_ticks // grid_resolution
    
    # Generate kick pattern
    kick_pattern = generate_kick_pattern(grid_positions, complexity, is_phonk)
    
    # Generate snare pattern
    snare_pattern = generate_snare_pattern(grid_positions, complexity, is_phonk)
    
    # Generate hi-hat pattern
    hihat_pattern = generate_hihat_pattern(grid_positions, complexity, is_phonk)
    
    # Generate additional percussion if complexity is high
    if complexity > 0.6:
        percussion_pattern = generate_percussion_pattern(grid_positions, complexity, is_phonk)
    else:
        percussion_pattern = [0] * grid_positions
    
    # Convert patterns to notes
    for i, has_kick in enumerate(kick_pattern):
        if has_kick:
            time = i * grid_resolution
            velocity = random.randint(100, 127)
            # Fixed duration to ensure consistent timing
            duration = min(grid_resolution, TICKS_PER_BEAT // 4)
            pattern.append((KICK, velocity, time, duration))
    
    for i, has_snare in enumerate(snare_pattern):
        if has_snare:
            time = i * grid_resolution
            velocity = random.randint(90, 115)
            # Fixed duration to ensure consistent timing
            duration = min(grid_resolution, TICKS_PER_BEAT // 4)
            
            # Randomly use clap or rim instead of snare for variation
            if random.random() < 0.2:
                note = CLAP if random.random() < 0.5 else RIM
            else:
                note = SNARE
                
            pattern.append((note, velocity, time, duration))
    
    for i, hat_type in enumerate(hihat_pattern):
        if hat_type > 0:
            time = i * grid_resolution
            
            if hat_type == 1:  # Closed hi-hat
                note = CLOSED_HAT
                velocity = random.randint(70, 100)
            elif hat_type == 2:  # Open hi-hat
                note = OPEN_HAT
                velocity = random.randint(80, 110)
            else:  # Pedal hi-hat
                note = PEDAL_HAT
                velocity = random.randint(60, 90)
            
            # Fixed duration to ensure consistent timing
            duration = min(grid_resolution, TICKS_PER_BEAT // 4)
            pattern.append((note, velocity, time, duration))
    
    for i, perc_type in enumerate(percussion_pattern):
        if perc_type > 0:
            time = i * grid_resolution
            
            if perc_type == 1:  # Tom
                note = random.choice([LOW_TOM, MID_TOM, HIGH_TOM])
                velocity = random.randint(80, 110)
            elif perc_type == 2:  # Crash
                note = CRASH
                velocity = random.randint(90, 120)
            else:  # Tambourine or other percussion
                note = TAMBOURINE
                velocity = random.randint(70, 100)
            
            # Fixed duration to ensure consistent timing
            duration = min(grid_resolution, TICKS_PER_BEAT // 4)
            pattern.append((note, velocity, time, duration))
    
    # Sort the pattern by time to ensure proper playback
    pattern.sort(key=lambda x: x[2])
    
    return pattern

def generate_kick_pattern(grid_positions, complexity, is_phonk):
    """
    Generate a kick drum pattern.
    
    Args:
        grid_positions (int): Number of grid positions
        complexity (float): Complexity of the pattern (0.0 to 1.0)
        is_phonk (bool): Whether to use phonk-style drums
        
    Returns:
        list: Boolean list indicating kick drum hits
    """
    pattern = [False] * grid_positions
    
    # Determine the base grid (how many positions per beat)
    positions_per_beat = 4 if complexity > 0.5 else 2
    
    # Place kicks on downbeats (first beat of each bar)
    for i in range(0, grid_positions, positions_per_beat * 4):
        pattern[i] = True
    
    # Add additional kicks based on complexity and style
    if is_phonk:
        # Phonk often has a double kick on the first beat
        for i in range(0, grid_positions, positions_per_beat * 4):
            if i + positions_per_beat // 2 < grid_positions:
                pattern[i + positions_per_beat // 2] = True
        
        # Add kicks on the third beat for phonk
        for i in range(positions_per_beat * 2, grid_positions, positions_per_beat * 4):
            pattern[i] = True
    else:
        # Standard patterns often have kicks on beats 1 and 3
        for i in range(0, grid_positions, positions_per_beat * 4):
            if i + positions_per_beat * 2 < grid_positions:
                pattern[i + positions_per_beat * 2] = True
    
    # Add additional kicks based on complexity
    if complexity > 0.4:
        # Add occasional syncopated kicks
        for i in range(positions_per_beat, grid_positions, positions_per_beat * 2):
            if random.random() < complexity * 0.5:
                pattern[i] = True
    
    if complexity > 0.7:
        # Add more complex kick patterns for high complexity
        for i in range(0, grid_positions, positions_per_beat):
            if not pattern[i] and random.random() < complexity * 0.3:
                pattern[i] = True
    
    return pattern

def generate_snare_pattern(grid_positions, complexity, is_phonk):
    """
    Generate a snare drum pattern.
    
    Args:
        grid_positions (int): Number of grid positions
        complexity (float): Complexity of the pattern (0.0 to 1.0)
        is_phonk (bool): Whether to use phonk-style drums
        
    Returns:
        list: Boolean list indicating snare drum hits
    """
    pattern = [False] * grid_positions
    
    # Determine the base grid (how many positions per beat)
    positions_per_beat = 4 if complexity > 0.5 else 2
    
    # Place snares on beats 2 and 4
    for i in range(positions_per_beat, grid_positions, positions_per_beat * 2):
        pattern[i] = True
    
    # Add additional snares based on complexity and style
    if is_phonk:
        # Phonk often has additional snares or claps
        for i in range(positions_per_beat * 3, grid_positions, positions_per_beat * 4):
            if random.random() < 0.7:
                pattern[i] = True
    
    # Add ghost notes and additional snares based on complexity
    if complexity > 0.6:
        for i in range(0, grid_positions, positions_per_beat // 2):
            if not pattern[i] and random.random() < complexity * 0.2:
                pattern[i] = True
    
    return pattern

def generate_hihat_pattern(grid_positions, complexity, is_phonk):
    """
    Generate a hi-hat pattern.
    
    Args:
        grid_positions (int): Number of grid positions
        complexity (float): Complexity of the pattern (0.0 to 1.0)
        is_phonk (bool): Whether to use phonk-style drums
        
    Returns:
        list: Integer list indicating hi-hat type (0=none, 1=closed, 2=open, 3=pedal)
    """
    pattern = [0] * grid_positions
    
    # Determine the base grid (how many positions per beat)
    positions_per_beat = 4 if complexity > 0.5 else 2
    
    # Basic hi-hat pattern - closed hats on each grid position
    for i in range(0, grid_positions, positions_per_beat // 2):
        pattern[i] = 1  # Closed hi-hat
    
    # Add open hi-hats based on complexity
    if complexity > 0.4:
        # Add occasional open hi-hats
        for i in range(positions_per_beat - 1, grid_positions, positions_per_beat * 2):
            if random.random() < complexity * 0.6:
                pattern[i] = 2  # Open hi-hat
    
    # Add pedal hi-hats for more complex patterns
    if complexity > 0.7:
        for i in range(positions_per_beat // 2, grid_positions, positions_per_beat * 2):
            if pattern[i] == 0 and random.random() < complexity * 0.4:
                pattern[i] = 3  # Pedal hi-hat
    
    # Adjust for phonk style if needed
    if is_phonk:
        # Phonk often has a distinctive hi-hat pattern
        for i in range(0, grid_positions, positions_per_beat * 2):
            if i + positions_per_beat // 2 < grid_positions:
                pattern[i + positions_per_beat // 2] = 2  # Open hi-hat
    
    return pattern

def generate_percussion_pattern(grid_positions, complexity, is_phonk):
    """
    Generate a percussion pattern.
    
    Args:
        grid_positions (int): Number of grid positions
        complexity (float): Complexity of the pattern (0.0 to 1.0)
        is_phonk (bool): Whether to use phonk-style drums
        
    Returns:
        list: Integer list indicating percussion type (0=none, 1=tom, 2=crash, 3=other)
    """
    pattern = [0] * grid_positions
    
    # Determine the base grid (how many positions per beat)
    positions_per_beat = 4 if complexity > 0.5 else 2
    
    # Add crash cymbals at the beginning of some bars
    for i in range(0, grid_positions, positions_per_beat * 4):
        if random.random() < 0.3:
            pattern[i] = 2  # Crash
    
    # Add toms and other percussion based on complexity
    if complexity > 0.6:
        # Add occasional toms
        for i in range(0, grid_positions, positions_per_beat):
            if pattern[i] == 0 and random.random() < complexity * 0.2:
                pattern[i] = 1  # Tom
    
    if complexity > 0.8:
        # Add other percussion for very complex patterns
        for i in range(0, grid_positions, positions_per_beat // 2):
            if pattern[i] == 0 and random.random() < complexity * 0.15:
                pattern[i] = 3  # Other percussion
    
    return pattern

def generate_complex_drum_pattern(num_bars, beats_per_bar, complexity=0.8, is_phonk=False):
    """
    Generate a more complex drum pattern with fills and variations.
    
    Args:
        num_bars (int): Number of bars
        beats_per_bar (int): Number of beats per bar
        complexity (float): Complexity of the pattern (0.0 to 1.0)
        is_phonk (bool): Whether to use phonk-style drums
        
    Returns:
        list: Drum pattern as (note, velocity, time, duration) tuples
    """
    # Generate a basic pattern first
    pattern = generate_drum_pattern(num_bars, beats_per_bar, complexity, is_phonk)
    
    # Calculate total ticks
    ticks_per_bar = beats_per_bar * TICKS_PER_BEAT
    total_ticks = num_bars * ticks_per_bar
    
    # Add fills at the end of every 4 bars or so
    for bar in range(3, num_bars, 4):  # Start at bar 4, then every 4 bars
        if bar * ticks_per_bar < total_ticks:
            # Generate a fill for the last beat of this bar
            fill_start = bar * ticks_per_bar + (beats_per_bar - 1) * TICKS_PER_BEAT
            fill_duration = TICKS_PER_BEAT
            
            # Generate the fill
            fill = generate_drum_fill(fill_duration, complexity)
            
            # Add the fill to the pattern with the correct time offset
            for note, velocity, time, duration in fill:
                pattern.append((note, velocity, fill_start + time, duration))
    
    # Sort the pattern by time to ensure proper playback
    pattern.sort(key=lambda x: x[2])
    
    return pattern

def generate_drum_fill(duration, intensity=0.8):
    """
    Generate a drum fill.
    
    Args:
        duration (int): Duration of the fill in ticks
        intensity (float): Intensity of the fill (0.0 to 1.0)
        
    Returns:
        list: Drum fill as (note, velocity, time, duration) tuples
    """
    fill = []
    
    # Use sixteenth notes for the fill
    grid_resolution = TICKS_PER_BEAT // 4
    
    # Number of grid positions
    grid_positions = duration // grid_resolution
    
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
            duration = min(grid_resolution, TICKS_PER_BEAT // 4)
            
            fill.append((note, velocity, time, duration))
    
    return fill

def generate_trap_fill(num_beats, intensity=0.8):
    """
    Generate a trap-style drum fill.
    
    Args:
        num_beats (int): Number of beats for the fill
        intensity (float): Intensity of the fill (0.0 to 1.0)
        
    Returns:
        list: Drum fill as (note, velocity, time, duration) tuples
    """
    fill = []
    
    # Calculate total ticks
    total_ticks = num_beats * TICKS_PER_BEAT
    
    # Use 32nd notes for the fill
    grid_resolution = TICKS_PER_BEAT // 8
    
    # Number of grid positions
    grid_positions = total_ticks // grid_resolution
    
    # Create a trap fill pattern
    for i in range(grid_positions):
        # Determine if we should place a note at this position
        # Higher probability towards the end for a build-up effect
        probability = 0.2 + (i / grid_positions) * intensity
        
        if random.random() < probability:
            time = i * grid_resolution
            
            # Choose a drum sound based on position
            if i % 8 == 0:
                # Downbeats get kicks
                note = KICK
                velocity = random.randint(100, 127)
            elif i % 4 == 0:
                # Quarter notes get snares or claps
                note = random.choice([SNARE, CLAP])
                velocity = random.randint(90, 120)
            elif i % 2 == 0:
                # Eighth notes get hi-hats
                note = random.choice([CLOSED_HAT, OPEN_HAT])
                velocity = random.randint(80, 110)
            else:
                # Other positions get various percussion
                note = random.choice([LOW_TOM, MID_TOM, HIGH_TOM, TAMBOURINE])
                velocity = random.randint(70, 100)
            
            # Add crescendo effect
            velocity = min(127, int(velocity * (0.7 + (i / grid_positions) * 0.3)))
            
            # Fixed duration to ensure consistent timing
            duration = min(grid_resolution, TICKS_PER_BEAT // 8)
            
            fill.append((note, velocity, time, duration))
    
    # Add a crash at the end
    fill.append((CRASH, 127, total_ticks - grid_resolution, grid_resolution))
    
    return fill