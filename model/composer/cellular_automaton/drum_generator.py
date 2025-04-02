import numpy as np
import random


class CellularAutomatonDrums:
    def __init__(self, bars, beats_per_bar, complexity, is_phonk, base_pattern=None):
        self.bars = bars
        self.beats_per_bar = beats_per_bar
        self.steps = bars * beats_per_bar * 4  # 16 steps per bar
        self.complexity = complexity
        self.is_phonk = is_phonk

        # Define drum instruments
        self.KICK = 0
        self.SNARE = 1
        self.CLOSED_HH = 2
        self.OPEN_HH = 3
        self.TOM = 4

        self.grid = np.zeros((5, self.steps), dtype=int)

        # If base_pattern is provided, start from it
        if base_pattern is not None:
            self.grid = base_pattern.copy()
        else:
            self._initialize_simple_pattern()

    def _initialize_simple_pattern(self):
        """Set up simple drum pattern (claps, hi-hats, light percussion)."""
        for i in range(self.steps):
            if i % 4 == 0:  # Claps/snare on beats 2 & 4
                self.grid[self.SNARE][i] = 1
            if i % 2 == 0:  # Hi-hats
                self.grid[self.CLOSED_HH][i] = 1

    def evolve_simple(self):
        """Apply rules for a simple groove (hi-hats, claps, minimal percussion)."""
        new_grid = self.grid.copy()

        for i in range(self.steps):
            # Hi-Hat Variation
            if i % 2 == 1 and random.random() < 0.1:
                new_grid[self.CLOSED_HH][i] = 0  # Remove hi-hats for groove

            # Open Hi-Hats (light usage)
            if i % 4 == 2 and random.random() < 0.2:
                new_grid[self.OPEN_HH][i] = 1  # Occasional open hi-hats

            # Clap Ghost Notes
            if i % 4 == 3 and random.random() < 0.15:
                new_grid[self.SNARE][i] = 1  # Extra ghost clap before snare

        self.grid = new_grid

    def evolve_complex(self):
        """Enhance a simple drum pattern with heavy kicks, ghost snares, and toms."""
        new_grid = self.grid.copy()

        for i in range(self.steps):
            # Kick Drum Enhancement
            if i % 4 == 0 or (random.random() < 0.3 and i % 4 == 3):
                new_grid[self.KICK][i] = 1  # Strong downbeat & syncopated kicks

            # More Ghost Snares
            if i % 4 == 3 and random.random() < 0.25:
                new_grid[self.SNARE][i] = 1  # Add ghost snares

            # Hi-Hat Rolls (Trap-style)
            if random.random() < 0.1:
                new_grid[self.CLOSED_HH][i] = 1  # Extra hi-hat hits for groove

            # Open Hi-Hats (More frequent)
            if i % 4 == 2 and random.random() < 0.4:
                new_grid[self.OPEN_HH][i] = 1

            # Tom Fills (Rare)
            if self.is_phonk and random.random() < 0.15:
                new_grid[self.TOM][i] = 1  # Add toms in Phonk mode

        self.grid = new_grid

    def get_pattern(self):
        """Convert grid to MIDI-style output."""
        drum_pattern = []
        for instrument_idx, instrument in enumerate([36, 38, 42, 46, 47]):  # Kick, Snare, Closed HH, Open HH, Tom
            for step in range(self.steps):
                if self.grid[instrument_idx][step]:
                    time = step * 120
                    velocity = random.randint(80, 120)
                    drum_pattern.append((instrument, velocity, time, 10))
        return drum_pattern


# Step 1: Generate a simple drum pattern
simple_drums = CellularAutomatonDrums(bars=4, beats_per_bar=4, complexity=0.4, is_phonk=False)
for _ in range(4):
    simple_drums.evolve_simple()

# Step 2: Generate a complex drum pattern using the simple one as a base
complex_drums = CellularAutomatonDrums(bars=4, beats_per_bar=4, complexity=0.7, is_phonk=True, base_pattern=simple_drums.grid)
for _ in range(4):
    complex_drums.evolve_complex()

# Print Results
print("Simple Drums:", simple_drums.get_pattern())
print("Complex Drums:", complex_drums.get_pattern())
