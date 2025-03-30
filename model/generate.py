import os
import sys
import pretty_midi
import numpy as np
import tensorflow as tf
import random
import sys
from .composer.music_generator import generate_music
from .composer.music_theory import MAJOR_SCALE, MINOR_SCALE
from .listen import midi_to_wav

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from transformer import Transformer

model_path = os.path.join(os.path.dirname(__file__), "z_transformer_model.keras")
transformer = tf.keras.models.load_model(model_path)

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
def generate_midi(tempo=120, output_file="standard", scale_type=0):
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

    note_not_found_counter = 0  # Counter for "no valid token found" cases
    MAX_TRIES = 10  # Maximum retries before restarting

    print(f"Starting token: {start_token} ({sequence[0]})")

    while start_time < total_duration:

        input_seq = np.array(sequence[-SEQ_LENGTH:])[None, :]
        target_seq = np.array(sequence[-(SEQ_LENGTH - 1):])[None, :]

        try:
            predictions = transformer(input_seq, target_seq, training=False).numpy()
        except Exception as e:
            print(f"[ERROR] Model prediction failed: {e}")
            break  # Stop if there's a model error

        last_logits = predictions[:, -1, :]
        probabilities = tf.nn.softmax(last_logits).numpy().flatten()

        # Sampling Method (Top-K with k=5)
        top_k_indices = np.argsort(probabilities)[-5:]

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
            note_not_found_counter += 1
            print(f"[WARN] No valid token found ({note_not_found_counter}/{MAX_TRIES}), retrying...")

            if note_not_found_counter >= MAX_TRIES:
                print("[ERROR] Too many failed attempts. Restarting script...\n")
                generate_midi(tempo)  # Restart the function
                return  # Ensure the current execution stops
            continue  # Retry the loop

        note_not_found_counter = 0  # Reset counter on success

        note_info = id_to_token[next_token_id]
        note_name, duration_str = note_info.split("_")
        duration = float(duration_str) * seconds_per_beat

        if start_time + duration > total_duration:
            print("[INFO] Reached total duration, stopping...")
            break

        pitch = max(21, min(108, pretty_midi.note_name_to_number(f"{note_name}4")))

        print(f"Generated Note: {note_name}, Duration: {duration:.2f}s, Pitch: {pitch}")

        if pitch == 21:
            melody_notes.append(pretty_midi.Note(
                velocity=0, pitch=pitch, start=start_time, end=start_time + duration
            ))
        else:
            melody_notes.append(pretty_midi.Note(
                velocity=100, pitch=pitch, start=start_time, end=start_time + duration
            ))

        sequence.append(next_token_id)
        start_time += duration

    print("\nComposition generated successfully!")
    
    # Convert `melody_notes` to required format
    midi_resolution = 480  # Standard MIDI resolution (ticks per beat)
    tick_values = np.array([240, 360, 480, 600])
    example_melody = []
    current_start_tick = 0  # Initialize start tick at zero

    for note in melody_notes:
        duration_ticks = int(midi.time_to_tick(note.end) - midi.time_to_tick(note.start))

        # Round to the closest allowed tick value
        rounded_duration = tick_values[np.abs(tick_values - duration_ticks).argmin()]

        # Append adjusted note with corrected start tick
        example_melody.append((note.pitch, note.velocity, current_start_tick, rounded_duration))

        # Update start tick for the next note
        current_start_tick += rounded_duration
    # Adjust total duration to exactly 3840
    total_duration = sum(d[3] for d in example_melody)

    if total_duration > 3860:
        while total_duration > 3860:
            example_melody.pop()
            total_duration = sum(d[3] for d in example_melody)
    else:
        i = 0
        while total_duration < 3860:
            if example_melody[i][3] == 240:
                example_melody[i] = (example_melody[i][0], example_melody[i][1], example_melody[i][2], 480)
                total_duration += 240
                i = (i + 1) % len(example_melody)
            # if example_melody[i]
            else:
                print("Loop Stuck")

    total_duration = sum(d[3] for d in example_melody)
    left_over = 3860 - total_duration
    if left_over > 0:
        last_note = example_melody[-1]
        updated_last_note = (last_note[0], last_note[1], last_note[2], last_note[3] + left_over)
        example_melody[-1] = updated_last_note

    total_duration = sum(d[3] for d in example_melody)

    print(f"\nConverted Melody (Adjusted to {total_duration} Ticks):")
    print(example_melody)

    # Define args
    if example_melody[0][0] == 21:
        root_note = 60
    else:
        root_note = example_melody[0][0]

    if scale_type == 0:
        scale_type = MAJOR_SCALE
    else:
        scale_type = MINOR_SCALE


    generate_music(
        output_file=f"{output_file}.mid",
        tempo=tempo,
        key=root_note,
        scale_type=scale_type,
        num_bars=44,
        style='trap',
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sf2_file = os.path.join(script_dir, "Sound Fonts", "Omega.sf2")
    midi_to_wav(f"{output_file}.mid", sf2_file, f"{output_file}.wav")





