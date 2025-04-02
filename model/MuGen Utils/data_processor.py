import os
import numpy as np
import pretty_midi
import music21
import glob
from tqdm import tqdm
import random
import pickle

# Configuration
class Config:
    # Input directories
    MIDI_DIR = "data/raw/midi/"
    KERN_DIR = "data/raw/kern/"
    
    # Output directory
    OUTPUT_DIR = "data/processed/"
    
    # Tokenization parameters
    MAX_PITCH = 108  # Highest MIDI pitch to consider
    MIN_PITCH = 21   # Lowest MIDI pitch to consider
    PITCH_CLASSES = 12  # Number of pitch classes (C, C#, etc.)
    OCTAVES = 10     # Number of octaves to consider
    
    # Duration quantization (in quarter notes)
    DURATION_BINS = [
        0.125,  # 32nd note
        0.25,   # 16th note
        0.375,  # dotted 16th
        0.5,    # 8th note
        0.75,   # dotted 8th
        1.0,    # quarter note
        1.5,    # dotted quarter
        2.0,    # half note
        3.0,    # dotted half
        4.0,    # whole note
        6.0,    # dotted whole
        8.0     # double whole
    ]
    
    # Velocity quantization
    VELOCITY_BINS = [16, 32, 48, 64, 80, 96, 112, 127]
    
    # Special tokens
    PAD_TOKEN = 0
    START_TOKEN = 1
    END_TOKEN = 2
    REST_TOKEN = 3
    
    # Token ranges
    PITCH_START_IDX = 4
    DURATION_START_IDX = PITCH_START_IDX + (MAX_PITCH - MIN_PITCH + 1)
    VELOCITY_START_IDX = DURATION_START_IDX + len(DURATION_BINS)
    VOCAB_SIZE = VELOCITY_START_IDX + len(VELOCITY_BINS)
    
    # Sequence parameters
    MAX_SEQ_LENGTH = 512
    MIN_SEQ_LENGTH = 16
    SEQUENCES_PER_FILE = 100

config = Config()

# Create output directory if it doesn't exist
os.makedirs(config.OUTPUT_DIR, exist_ok=True)

# Save vocabulary mapping for later use
def save_vocabulary():
    vocab = {
        "pad_token": config.PAD_TOKEN,
        "start_token": config.START_TOKEN,
        "end_token": config.END_TOKEN,
        "rest_token": config.REST_TOKEN,
        "pitch_start_idx": config.PITCH_START_IDX,
        "duration_start_idx": config.DURATION_START_IDX,
        "velocity_start_idx": config.VELOCITY_START_IDX,
        "vocab_size": config.VOCAB_SIZE,
        "pitch_range": (config.MIN_PITCH, config.MAX_PITCH),
        "duration_bins": config.DURATION_BINS,
        "velocity_bins": config.VELOCITY_BINS
    }
    
    with open(os.path.join(config.OUTPUT_DIR, "vocabulary.pkl"), "wb") as f:
        pickle.dump(vocab, f)
    
    print(f"Vocabulary saved with {config.VOCAB_SIZE} tokens")

# Process MIDI files
def process_midi_files():
    midi_files = glob.glob(os.path.join(config.MIDI_DIR, "**/*.mid"), recursive=True)
    midi_files.extend(glob.glob(os.path.join(config.MIDI_DIR, "**/*.midi"), recursive=True))
    
    if not midi_files:
        print(f"No MIDI files found in {config.MIDI_DIR}")
        return []
    
    print(f"Processing {len(midi_files)} MIDI files...")
    
    all_sequences = []
    
    for midi_file in tqdm(midi_files):
        try:
            # Load MIDI file
            midi_data = pretty_midi.PrettyMIDI(midi_file)
            
            # Extract monophonic melody from the highest part
            # (In a real scenario, you might want a more sophisticated melody extraction)
            melody_notes = []
            
            for instrument in midi_data.instruments:
                if not instrument.is_drum:  # Skip drum tracks
                    for note in instrument.notes:
                        melody_notes.append(note)
            
            # Sort by start time, then by pitch (higher pitch first for tied notes)
            melody_notes.sort(key=lambda x: (x.start, -x.pitch))
            
            # Convert to monophonic by keeping only the highest note at each time point
            monophonic_notes = []
            current_end = 0
            
            for note in melody_notes:
                if note.start >= current_end:
                    # Only add notes that don't overlap with previous notes
                    monophonic_notes.append(note)
                    current_end = note.end
            
            # Convert notes to tokens
            tokens = convert_notes_to_tokens(monophonic_notes, midi_data.get_tempo_changes())
            
            # Split into sequences
            sequences = split_into_sequences(tokens)
            all_sequences.extend(sequences)
            
        except Exception as e:
            print(f"Error processing {midi_file}: {e}")
    
    return all_sequences

# Process Kern files
def process_kern_files():
    kern_files = glob.glob(os.path.join(config.KERN_DIR, "**/*.krn"), recursive=True)
    
    if not kern_files:
        print(f"No Kern files found in {config.KERN_DIR}")
        return []
    
    print(f"Processing {len(kern_files)} Kern files...")
    
    all_sequences = []
    
    for kern_file in tqdm(kern_files):
        try:
            # Parse Kern file with music21
            score = music21.converter.parse(kern_file)
            
            # Extract the highest part (usually melody)
            melody_part = None
            highest_part_avg_pitch = -1
            
            for part in score.parts:
                # Calculate average pitch for this part
                pitches = [n.pitch.midi for n in part.flat.notes if hasattr(n, 'pitch')]
                if pitches:
                    avg_pitch = sum(pitches) / len(pitches)
                    if avg_pitch > highest_part_avg_pitch:
                        highest_part_avg_pitch = avg_pitch
                        melody_part = part
            
            if melody_part is None:
                continue
            
            # Convert to pretty_midi format for consistent processing
            midi_stream = music21.midi.translate.streamToMidiFile(melody_part)
            midi_file = music21.midi.translate.midiFileToStream(midi_stream)
            
            # Extract tempo information
            tempo_changes = []
            for mm in score.flat.getElementsByClass('MetronomeMark'):
                tempo_changes.append((mm.offset, mm.number))
            
            # Convert notes to tokens
            notes = []
            for note in melody_part.flat.notes:
                if hasattr(note, 'pitch'):  # Skip chords, get only individual notes
                    midi_note = pretty_midi.Note(
                        velocity=80,  # Default velocity
                        pitch=note.pitch.midi,
                        start=note.offset,
                        end=note.offset + note.duration.quarterLength
                    )
                    notes.append(midi_note)
            
            # Sort notes by start time
            notes.sort(key=lambda x: x.start)
            
            # Convert to tokens
            tokens = convert_notes_to_tokens(notes, tempo_changes)
            
            # Split into sequences
            sequences = split_into_sequences(tokens)
            all_sequences.extend(sequences)
            
        except Exception as e:
            print(f"Error processing {kern_file}: {e}")
    
    return all_sequences

# Convert notes to tokens
def convert_notes_to_tokens(notes, tempo_changes=None):
    if not notes:
        return []
    
    tokens = [config.START_TOKEN]  # Start with START token
    
    prev_end = notes[0].start
    
    for note in notes:
        # Add rest if there's a gap
        if note.start > prev_end + 0.1:  # Small threshold to account for rounding errors
            tokens.append(config.REST_TOKEN)
        
        # Add pitch token
        if config.MIN_PITCH <= note.pitch <= config.MAX_PITCH:
            pitch_token = config.PITCH_START_IDX + (note.pitch - config.MIN_PITCH)
            tokens.append(pitch_token)
        
        # Add duration token
        duration = note.end - note.start
        duration_bin = min(range(len(config.DURATION_BINS)), 
                          key=lambda i: abs(config.DURATION_BINS[i] - duration))
        duration_token = config.DURATION_START_IDX + duration_bin
        tokens.append(duration_token)
        
        # Add velocity token
        velocity_bin = min(range(len(config.VELOCITY_BINS)), 
                          key=lambda i: abs(config.VELOCITY_BINS[i] - note.velocity))
        velocity_token = config.VELOCITY_START_IDX + velocity_bin
        tokens.append(velocity_token)
        
        prev_end = note.end
    
    tokens.append(config.END_TOKEN)  # End with END token
    
    return tokens

# Split tokens into sequences
def split_into_sequences(tokens):
    if len(tokens) < config.MIN_SEQ_LENGTH:
        return []
    
    sequences = []
    
    # For very long token sequences, split into multiple sequences
    if len(tokens) > config.MAX_SEQ_LENGTH:
        # Find natural breaking points (END tokens)
        break_points = [i for i, t in enumerate(tokens) if t == config.END_TOKEN]
        
        start_idx = 0
        for end_idx in break_points:
            if end_idx - start_idx >= config.MIN_SEQ_LENGTH:
                # Add START token if not at the beginning
                seq = tokens[start_idx:end_idx+1]
                if seq[0] != config.START_TOKEN:
                    seq = [config.START_TOKEN] + seq
                
                # Add END token if not at the end
                if seq[-1] != config.END_TOKEN:
                    seq = seq + [config.END_TOKEN]
                
                sequences.append(seq)
                
                # Move start index to after this sequence
                start_idx = end_idx + 1
    else:
        # Just add the whole sequence
        sequences.append(tokens)
    
    return sequences

# Augment a sequence for data augmentation
def augment_sequence(sequence, pitch_shift_range=(-6, 6), tempo_change_range=(0.8, 1.2)):
    # Copy the sequence to avoid modifying the original
    augmented = sequence.copy()
    
    # Apply pitch shift
    pitch_shift = random.randint(pitch_shift_range[0], pitch_shift_range[1])
    
    for i in range(len(augmented)):
        token = augmented[i]
        
        # Only shift pitch tokens
        if config.PITCH_START_IDX <= token < config.DURATION_START_IDX:
            # Calculate new pitch
            pitch_idx = token - config.PITCH_START_IDX
            new_pitch_idx = pitch_idx + pitch_shift
            
            # Ensure it's within range
            max_pitch_idx = config.MAX_PITCH - config.MIN_PITCH
            if 0 <= new_pitch_idx <= max_pitch_idx:
                augmented[i] = config.PITCH_START_IDX + new_pitch_idx
    
    # Apply tempo change (affects duration tokens)
    tempo_change = random.uniform(tempo_change_range[0], tempo_change_range[1])
    
    for i in range(len(augmented)):
        token = augmented[i]
        
        # Only change duration tokens
        if config.DURATION_START_IDX <= token < config.VELOCITY_START_IDX:
            # Calculate duration bin index
            duration_idx = token - config.DURATION_START_IDX
            
            # Apply tempo change
            original_duration = config.DURATION_BINS[duration_idx]
            new_duration = original_duration * tempo_change
            
            # Find closest duration bin
            new_duration_idx = min(range(len(config.DURATION_BINS)), 
                                  key=lambda i: abs(config.DURATION_BINS[i] - new_duration))
            
            augmented[i] = config.DURATION_START_IDX + new_duration_idx
    
    return augmented

# Save sequences to files
def save_sequences(sequences):
    if not sequences:
        print("No sequences to save")
        return
    
    print(f"Saving {len(sequences)} sequences...")
    
    # Shuffle sequences for better distribution
    random.shuffle(sequences)
    
    # Split into files
    num_files = (len(sequences) + config.SEQUENCES_PER_FILE - 1) // config.SEQUENCES_PER_FILE
    
    for i in range(num_files):
        start_idx = i * config.SEQUENCES_PER_FILE
        end_idx = min((i + 1) * config.SEQUENCES_PER_FILE, len(sequences))
        
        file_sequences = sequences[start_idx:end_idx]
        
        # Save to pickle file instead of numpy to handle variable-length sequences
        output_file = os.path.join(config.OUTPUT_DIR, f"sequences_{i:04d}.pkl")
        with open(output_file, 'wb') as f:
            pickle.dump(file_sequences, f)
    
    print(f"Saved sequences to {num_files} files in {config.OUTPUT_DIR}")

# Load and preprocess dataset (used by training script)
def load_and_preprocess_dataset():
    # Load all preprocessed files
    file_pattern = os.path.join(config.OUTPUT_DIR, "*.pkl")
    files = glob.glob(file_pattern)
    
    if not files:
        raise ValueError(f"No data files found in {config.OUTPUT_DIR}")
    
    all_sequences = []
    
    for file in files:
        with open(file, 'rb') as f:
            sequences = pickle.load(f)
            all_sequences.extend(sequences)
    
    return all_sequences

# Main processing function
def process_all_data():
    # Save vocabulary first
    save_vocabulary()
    
    # Process MIDI files
    midi_sequences = process_midi_files()
    
    # Process Kern files
    kern_sequences = process_kern_files()
    
    # Combine all sequences
    all_sequences = midi_sequences + kern_sequences
    
    if not all_sequences:
        print("No sequences were generated. Check your input data.")
        return
    
    print(f"Generated {len(all_sequences)} sequences in total")
    
    # Save sequences
    save_sequences(all_sequences)
    
    print("Data processing complete!")

if __name__ == "__main__":
    process_all_data()