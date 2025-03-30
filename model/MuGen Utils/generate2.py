"""
🔬 Theory Behind Melody Generation Improvements
To improve the melody generation, let's break down the required enhancements into several key areas:

🎸 1. Dynamic Instrument Selection
Instead of always using a piano sound (program=0 in MIDI), we can dynamically assign an instrument based on user input or melody type.

💡 Why?
Different instruments suit different musical contexts.
Example:
Piano → Best for solo melodies & chords
Strings (e.g., Violin, Cello) → Emotional, legato phrases
Synths → Electronic, futuristic vibes
Bass Guitar → Strong foundation for bass lines
🎼 MIDI Instrument Mapping
MIDI provides 128 instrument sounds, categorized as:

🎹 Piano (0–7)
🎸 Guitars (24–31)
🎷 Woodwinds (72–79)
🎻 Strings (40–47)
🎺 Brass (56–63)
🎛 Synths (80–95)
🔹 Implementation Idea:

Allow user input ("instrument": "violin")
Or, auto-assign based on melody type (e.g., "bass" → Bass Guitar)
🎚 2. Sampling Methods (Top-K & Temperature Sampling)
A crucial part of AI music generation is controlling randomness in note selection.

🔀 a) Top-K Sampling
Instead of choosing the most probable note, we restrict choices to the top K most probable notes.
🎯 Effect: Prevents repetitive, "boring" melodies by adding some controlled randomness.
🎼 Example:
K=1 → Always picks the most likely note (deterministic, predictable).
K=5 → Allows variation while keeping the melody structured.
K=20+ → More randomness, can sound chaotic.
🔥 b) Temperature-Based Sampling
Temperature adjusts the probability distribution:
Low temperature (0.3) → Predictable, structured melody
Medium temperature (0.7) → Balanced creativity & structure
High temperature (1.5) → Chaotic, experimental melodies
🔹 Implementation Idea:

Let the user choose "top-k" or "temperature" before generation.
Provide an adjustable K-value and temperature setting.
🎵 3. Melody Types (Main, Bass, Arpeggiation)
Each type of melody has a distinct role in music. We can generate different types dynamically:

a) Main Melody
Role: The primary musical phrase.
Characteristics:
Medium-range pitches
Balanced rhythm
Moderate note duration
Best Instruments: 🎹 Piano, 🎻 Violin, 🎺 Trumpet
b) Bass Melody
Role: Creates a harmonic foundation.
Characteristics:
Lower octave (C2–C4)
Longer notes (half & whole notes)
Often follows the root notes of the chord
Best Instruments: 🎸 Bass Guitar, 🎻 Cello, 🎷 Saxophone
c) Arpeggiation
Role: A broken chord pattern (playing chord notes one at a time instead of all together).
Characteristics:
Fast note sequences (16th/8th notes)
Notes move in ascending/descending chord patterns
Octave variations for complexity
Best Instruments: 🎹 Piano, 🎛 Synth, 🎸 Electric Guitar
🔹 Implementation Idea:

User selects "Main", "Bass", or "Arpeggiation"
Modify note generation rules accordingly.
🎛 4. MIDI Modifications for a More Realistic Sound
AI-generated melodies often sound "robotic" due to lack of human-like imperfections. We can improve this by applying MIDI effects.

🎧 a) Reverb (Echo-Like Effect)
Simulates natural acoustics (large hall, small room).
In MIDI, CC91 (Reverb Send Level) controls this.
Example:
python
Copy
Edit
midi_file.instruments[0].control_changes.append(
    pretty_midi.ControlChange(number=91, value=80, time=0)
)
Effect: Adds depth & realism.
🎵 b) Delay / Echo
Repeats a note after a slight delay.
Can be simulated by adding a lower-velocity duplicate note a few beats later.
🎸 c) Distortion (Electric Guitar)
Adds a gritty, overdriven sound (for rock & electronic music).
Some MIDI synths allow distortion control.
🎼 d) Chord Variations
Instead of single notes, generate chord-based melodies (e.g., triads, seventh chords).
Example:
If the AI generates a note "C4", also add "E4" and "G4" (C major chord).
🔹 Implementation Idea:

Use MIDI Control Changes for reverb, echo.
Apply chord structures dynamically.
🔚 5. Smarter Ending Notes
A good melody should resolve naturally. The last notes should feel intentional, not abrupt.

💡 Solution
Final note = C in the same octave as the second-last note
Second-last note = slightly longer than the last note
Final note should have a slightly lower velocity for a softer resolution.
🔹 Implementation Idea:

Store the second-last note's octave.
Generate final note as a C in that octave.
Adjust note durations:
Second-last note → 1.2× the standard duration.
Final note → Shorter than second-last.
💡 Summary of Enhancements
Feature	Why?	Implementation
🎸 Dynamic Instruments	Adds variety & realism	Select based on melody type
🎚 Sampling (Top-K, Temperature)	Controls randomness	User selects mode
🎵 Melody Type (Main, Bass, Arp.)	Creates different musical roles	Rules for each type
🎛 MIDI Effects (Reverb, Delay, Chords)	Enhances realism	Add MIDI CC + chords
🎼 Better Ending Note	Smooth melody resolution	Inspired by second-last note
"""


import pretty_midi
import numpy as np
import tensorflow as tf
import random
from composer.music_generator import generate_full_composition

# Load trained Transformer model
transformer = tf.keras.models.load_model("z_transformer_model.keras")

# Token mappings
token_to_id = {
    'A_0.25': 1, 'A_0.50': 2, 'A_0.75': 3, 'A_1.00': 4, 'A_1.50': 5, 'A_2.00': 6,
    'B-_0.25': 7, 'B-_0.50': 8, 'B-_0.75': 9, 'B-_1.00': 10, 'B-_2.00': 11, 
    'B_0.25': 12, 'B_0.50': 13, 'B_0.75': 14, 'B_1.00': 15, 'B_1.50': 16, 'B_2.00': 17, 
    'C_0.25': 20, 'C_0.50': 21, 'C_0.75': 22, 'C_1.00': 23, 'C_1.50': 24, 'C_2.00': 25,
    'D_0.25': 26, 'D_0.50': 27, 'D_0.75': 28, 'D_1.00': 29, 'D_1.50': 30, 'D_2.00': 31,
    'E_0.25': 35, 'E_0.50': 36, 'E_0.75': 37, 'E_1.00': 38, 'E_1.50': 39, 'E_2.00': 40,
    'F_0.25': 46, 'F_0.50': 47, 'F_0.75': 48, 'F_1.00': 49, 'F_1.50': 50, 'F_2.00': 51,
    'G_0.25': 54, 'G_0.50': 55, 'G_0.75': 56, 'G_1.00': 57, 'G_1.50': 58, 'G_2.00': 59
}
id_to_token = {v: k for k, v in token_to_id.items()}

# Function to generate a short MIDI melody (4 bars)
def generate_midi(tempo=120):


    print(f"Generating 4 bars of music at {tempo} BPM... 🎵")

    # MIDI Setup
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)  # Default: Piano

    beats_per_second = tempo / 60.0
    seconds_per_beat = 1.0 / beats_per_second
    total_duration = 4 * 4 * seconds_per_beat  # 4 bars in 4/4 time

    # Start sequence
    start_token = random.choice(list(token_to_id.keys()))
    sequence = [token_to_id[start_token]]

    start_time = 0.0
    melody_notes = []
    SEQ_LENGTH = 16  # Shorter sequence length for 4 bars

    print(f"Starting token: {start_token} ({sequence[0]})")

    while start_time < total_duration:
        # print(f"\n[INFO] Generating note at {start_time:.2f} seconds...")

        input_seq = np.array(sequence[-SEQ_LENGTH:])[None, :]
        target_seq = np.array(sequence[-(SEQ_LENGTH - 1):])[None, :]

        # print(f"Input sequence: {input_seq}")

        try:
            predictions = transformer(input_seq, target_seq, training=False).numpy()
            # print(f"Predictions shape: {predictions.shape}")
        except Exception as e:
            print(f"[ERROR] Model prediction failed: {e}")
            break  # Stop if there's a model error

        # Ensure correct logits extraction
        last_logits = predictions[:, -1, :]
        # print(f"Last logits: {last_logits}")

        # Apply softmax to logits
        probabilities = tf.nn.softmax(last_logits).numpy().flatten()
        # print(f"Probabilities: {probabilities}")

        # Sampling Method (Top-K with k=5)
        top_k_indices = np.argsort(probabilities)[-5:]  # Get top 5 tokens
        # print(f"Top-K token candidates: {top_k_indices}")

        # Choose a valid token (rejecting 0.25 and 2.00 duration)
        next_token_id = None
        for token in np.random.choice(top_k_indices, size=len(top_k_indices), replace=False):
            if token in id_to_token:
                note_info = id_to_token[token]
                _, duration_str = note_info.split("_")
                duration = float(duration_str) * seconds_per_beat

                # Accept only 0.50, 1.00, and 1.50 beat notes
                if 0.50 * seconds_per_beat <= duration <= 1.50 * seconds_per_beat:
                    next_token_id = token
                    break

        if next_token_id is None:
            print("[WARN] No valid token found, retrying...")
            continue  # Retry the loop

        # print(f"Chosen token ID: {next_token_id} ({id_to_token[next_token_id]})")

        # Decode the token
        note_info = id_to_token[next_token_id]
        note_name, duration_str = note_info.split("_")
        duration = float(duration_str) * seconds_per_beat

        if start_time + duration > total_duration:
            print("[INFO] Reached total duration, stopping...")
            break

        pitch = max(21, min(108, pretty_midi.note_name_to_number(f"{note_name}4")))

        print(f"Generated Note: {note_name}, Duration: {duration:.2f}s, Pitch: {pitch}")

        melody_notes.append(pretty_midi.Note(
            velocity=100, pitch=pitch, start=start_time, end=start_time + duration
        ))

        sequence.append(next_token_id)
        start_time += duration

    # Final Note Adjustment
    if melody_notes:
        melody_notes[-1].velocity = 80  # Softer ending

    instrument.notes.extend(melody_notes)
    midi.instruments.append(instrument)
    print(melody_notes)
    # midi.write("latest_melody.mid")

    print("MIDI file 'latest_melody.mid' created successfully!")

# Run generator
generate_midi()





"""I have a melody generation script (generate.py) that uses a Transformer model to generate MIDI files. The current script has some limitations, and I want to enhance it with the following features:

1️⃣ Dynamic Instrument Selection:

Allow user input for instrument choice OR auto-assign based on melody type.
Use MIDI instrument mapping (Piano, Strings, Synths, Bass, etc.).
2️⃣ Improved Sampling Methods:

Implement Top-K Sampling (restricts note selection to K most probable notes).
Implement Temperature-Based Sampling (controls randomness in note selection).
User should be able to choose between "top-k" or "temperature" mode.
3️⃣ Melody Type Selection:

Allow user to select between Main Melody, Bass Line, or Arpeggiation.
Implement different note generation rules for each melody type.
4️⃣ MIDI Enhancements for Realism:

Add reverb, delay (echo), distortion, and dynamic chord variations to improve musical quality.
Use MIDI Control Change (CC) messages where applicable.
5️⃣ Smarter Ending Notes:

The second-last note should be slightly longer than the last note.
The final note should be a C in the same octave as the second-last note for a more natural resolution.
The final note should also have a softer velocity for a smoother ending.
📜 Next Step:
I will provide my current generate.py code. Please modify it to include all the above enhancements. 🚀🎶



20 Procedural Ways to Improve Music Composition
These will increase interest without losing structure.

Melody & Harmony Enhancements
Call & Response – Have one melody ask a question and another answer it.

Counterpoint – A moving secondary melody that complements the main melody.

Melodic Automation – Add pitch bends or vibrato in certain sections.

Phrase Extension – Occasionally stretch a phrase to 5 or 7 bars instead of 4.

Tension & Release – Use dissonance before resolving into a consonant chord.

Rhythm & Drums Enhancements
Polyrhythms – Layer 3 over 4 rhythms for more groove.

Swing & Shuffle – Slightly shift note timing to make it feel more human.

Ghost Notes – Add subtle low-velocity snare & hi-hat hits for groove.

Syncopation – Delay the expected beat for unexpected rhythmic patterns.

Drum Fills Variation – Use different fills for each phrase (not just the same one).

Bass & Low-End Enhancements
Bass Glide – Use a portamento slide between bass notes.

Sub-Bass Layering – Add an octave lower deep sine wave bass.

Funk Grooves – Use off-beat bass plucks instead of just root notes.

Octave Jumps – Occasionally jump an octave for energy.

Bass Mute Notes – Short, percussive bass notes between beats.

Structural Enhancements
Dynamic Volume Changes – Make sections gradually build or drop in energy.

Instrument Layering – Introduce strings, pads, or synths slowly.

Tempo Shifts – Speed up or slow down slightly in a build-up.

Reverse Reverb – Play a reversed reverb tail before an instrument comes in.

Unexpected Key Change – Switch key in the last chorus for a surprising lift.
"""