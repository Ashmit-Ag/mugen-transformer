import tensorflow as tf
import numpy as np
import json
from transformer import Transformer  # Import your Transformer model

# ==== Load Processed Dataset ====
with open("processed_dataset.json", "r") as f:
    dataset = json.load(f)

# ==== Tokenization & Preprocessing ====
all_tokens = sorted(set(token for sequence in dataset for token in sequence))
token_to_id = {token: i for i, token in enumerate(all_tokens, start=1)}  # Reserve 0 for padding
id_to_token = {i: token for token, i in token_to_id.items()}
print(token_to_id)

VOCAB_SIZE = len(token_to_id) + 1  # Include an extra index for padding
SEQ_LENGTH = max(len(seq) for seq in dataset)  # Max sequence length

# Convert dataset into tokenized integer sequences
def tokenize_sequence(sequence):
    return [token_to_id[token] for token in sequence]

tokenized_data = [tokenize_sequence(seq) for seq in dataset]

# Pad sequences to SEQ_LENGTH
tokenized_data = tf.keras.preprocessing.sequence.pad_sequences(
    tokenized_data, maxlen=SEQ_LENGTH, padding="post"
)

# ==== Create TensorFlow Dataset ====
BATCH_SIZE = 64
BUFFER_SIZE = 1000

def prepare_data(sequence):
    """
    Creates (input, target) pairs by shifting the sequence for next-token prediction.
    """
    input_seq = sequence[:-1]  # Input is everything except last token
    target_seq = sequence[1:]  # Target is everything except first token
    return tf.convert_to_tensor(input_seq, dtype=tf.int32), tf.convert_to_tensor(target_seq, dtype=tf.int32)

# Debugging: Check if dataset contains valid sequences
print(f"Total sequences in dataset: {len(tokenized_data)}")

train_dataset = (
    tf.data.Dataset.from_tensor_slices(tokenized_data)
    .map(prepare_data)
    .shuffle(BUFFER_SIZE, reshuffle_each_iteration=True)  # Ensure it reshuffles
    .repeat()  # 🔥 Make dataset infinite to prevent "End of sequence"
    .batch(BATCH_SIZE, drop_remainder=False)  # Keep all data
)

# ==== Define Transformer Model ====
transformer = Transformer(
    num_layers=2,
    d_model=64,
    num_heads=2,
    d_feedforward=128,
    input_vocab_size=VOCAB_SIZE,
    target_vocab_size=VOCAB_SIZE,
    max_num_positions_in_pe_encoder=SEQ_LENGTH,
    max_num_positions_in_pe_decoder=SEQ_LENGTH,
    dropout_rate=0.1,
)

# Define Loss Function with Padding Mask
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction="none")
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

def masked_loss(target, pred):
    mask = tf.cast(target != 0, dtype=tf.float32)  # Ignore padding tokens
    loss = loss_fn(target, pred) * mask  # Apply mask


    return tf.reduce_mean(loss)  # Compute mean only on valid tokens


@tf.function
def train_step(input_seq, target_seq):
    with tf.GradientTape() as tape:
        predictions = transformer(input_seq, target_seq, training=True)  # 🔥 Pass `target_seq`
        loss = masked_loss(target_seq, predictions)  

    gradients = tape.gradient(loss, transformer.trainable_variables)
    optimizer.apply_gradients(zip(gradients, transformer.trainable_variables))

    return loss

sample_input = tf.convert_to_tensor(tokenized_data[:1], dtype=tf.int32)  # Single input sequence
sample_target = tf.convert_to_tensor(tokenized_data[:1], dtype=tf.int32)  # Dummy target sequence

sample_output = transformer(sample_input, sample_target, training=False)  # Pass both input & target


EPOCHS = 2
for epoch in range(EPOCHS):
    total_loss = 0
    num_batches = 0

    for batch, (input_seq, target_seq) in enumerate(train_dataset):
        loss = train_step(input_seq, target_seq)
        total_loss += loss.numpy()
        num_batches += 1

        # Print progress every 10 batches
        if batch % 10 == 0:
            print(f"Epoch {epoch+1}, Batch {batch}, Loss: {loss.numpy():.4f}")
        if batch > 1000:
            break
    
    avg_loss = total_loss / max(1, num_batches)  # Avoid division by zero
    print(f"Epoch {epoch+1} completed. Average Loss: {avg_loss:.6f}\n")

# ==== Save the Model ====
transformer.save("transformer_model.keras")
