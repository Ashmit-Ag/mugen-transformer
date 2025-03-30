import numpy as np
import tensorflow as tf
from keras.layers import (
    Dense,
    Dropout,
    Embedding,
    LayerNormalization,
    MultiHeadAttention,
)


def sinusoidal_position_encoding(num_positions, d_model):
    """Create sinusoidal positional encoding."""
    angles = _get_angles(
        np.arange(num_positions)[:, np.newaxis],
        np.arange(d_model)[np.newaxis, :],
        d_model,
    )

    sines = np.sin(angles[:, 0::2])
    cosines = np.cos(angles[:, 1::2])

    pos_encoding = np.concatenate([sines, cosines], axis=-1)
    pos_encoding = pos_encoding[np.newaxis, ...]  # (1, position, d_model)

    return tf.cast(pos_encoding, dtype=tf.float32)


def _get_angles(pos, i, d_model):
    """Calculate angles for positional encoding."""
    angle_dropout_rates = 1 / np.power(
        10000, (2 * (i // 2)) / np.float32(d_model)
    )
    return pos * angle_dropout_rates


class Transformer(tf.keras.Model):
    """
    Transformer model for monophonic melody generation.
    Modified to work with autoregressive generation.
    """

    def __init__(
        self,
        num_layers,
        d_model,
        num_heads,
        d_feedforward,
        input_vocab_size,
        target_vocab_size,
        max_num_positions_in_pe_encoder,
        max_num_positions_in_pe_decoder,
        dropout_rate=0.1,
        **kwargs
    ):
        super(Transformer, self).__init__(**kwargs)

        self.num_layers = num_layers
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_feedforward = d_feedforward
        self.input_vocab_size = input_vocab_size
        self.target_vocab_size = target_vocab_size
        self.max_num_positions_in_pe_encoder = max_num_positions_in_pe_encoder
        self.max_num_positions_in_pe_decoder = max_num_positions_in_pe_decoder
        self.dropout_rate = dropout_rate

        self.encoder = Encoder(
            num_layers, d_model, num_heads, d_feedforward,
            input_vocab_size, max_num_positions_in_pe_encoder, dropout_rate
        )
        self.decoder = Decoder(
            num_layers, d_model, num_heads, d_feedforward,
            target_vocab_size, max_num_positions_in_pe_decoder, dropout_rate
        )

        self.final_layer = Dense(target_vocab_size)

    def call(self, input, target, training=False, enc_padding_mask=None, look_ahead_mask=None, dec_padding_mask=None):
        """
        Forward pass of Transformer model.
        For melody generation, we use a simplified version where the encoder input can be a dummy token.
        """
        # For autoregressive generation, we can use a dummy encoder input
        if tf.shape(input)[1] == 1 and tf.shape(target)[1] > 1:
            # Create a dummy encoder output of the right shape
            batch_size = tf.shape(target)[0]
            enc_output = tf.zeros((batch_size, 1, self.d_model))
        else:
            # Normal encoder-decoder operation
            enc_output = self.encoder(input, training=training, mask=enc_padding_mask)
        
        dec_output = self.decoder(target, enc_output, training=training, look_ahead_mask=look_ahead_mask, padding_mask=dec_padding_mask)
        return self.final_layer(dec_output)

    def get_config(self):
        """
        Enables saving and reloading the model.
        """
        config = super(Transformer, self).get_config()
        config.update({
            "num_layers": self.num_layers,
            "d_model": self.d_model,
            "num_heads": self.num_heads,
            "d_feedforward": self.d_feedforward,
            "input_vocab_size": self.input_vocab_size,
            "target_vocab_size": self.target_vocab_size,
            "max_num_positions_in_pe_encoder": self.max_num_positions_in_pe_encoder,
            "max_num_positions_in_pe_decoder": self.max_num_positions_in_pe_decoder,
            "dropout_rate": self.dropout_rate,
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


class Encoder(tf.keras.layers.Layer):
    """Transformer Encoder."""

    def __init__(
        self,
        num_layers,
        d_model,
        num_heads,
        d_feedforward,
        input_vocab_size,
        maximum_positions_in_pe,
        dropout_rate=0.1,
    ):
        super(Encoder, self).__init__()
        self.d_model = d_model
        self.num_layers = num_layers

        self.embedding = Embedding(input_vocab_size, d_model)
        self.pos_encoding = sinusoidal_position_encoding(
            maximum_positions_in_pe, d_model
        )
        self.enc_layers = [
            EncoderLayer(d_model, num_heads, d_feedforward, dropout_rate)
            for _ in range(num_layers)
        ]
        self.dropout = Dropout(dropout_rate)

    def call(self, x, training, mask):
        """Forward pass of Encoder."""
        x = self.embedding(x)  # (batch_size, input_seq_len, d_model)
        x *= tf.math.sqrt(tf.cast(self.d_model, x.dtype))

        sliced_pos_encoding = self._get_sliced_positional_encoding(x)
        x = tf.cast(x, dtype=tf.float32)
        x += sliced_pos_encoding

        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x = self.enc_layers[i](x, training=training, mask=mask)

        return x  # (batch_size, input_seq_len, d_model)

    def _get_sliced_positional_encoding(self, x):
        """Get positional encoding sliced to the right length."""
        return self.pos_encoding[:, :tf.shape(x)[1], :]


class Decoder(tf.keras.layers.Layer):
    """Transformer Decoder."""

    def __init__(
        self,
        num_layers,
        d_model,
        num_heads,
        d_feedforward,
        target_vocab_size,
        maximum_positions_in_pe,
        dropout_rate=0.1,
    ):
        super(Decoder, self).__init__()
        self.d_model = d_model
        self.num_layers = num_layers

        self.embedding = Embedding(target_vocab_size, d_model)
        self.pos_encoding = sinusoidal_position_encoding(
            maximum_positions_in_pe, d_model
        )

        self.dec_layers = [
            DecoderLayer(d_model, num_heads, d_feedforward, dropout_rate)
            for _ in range(num_layers)
        ]
        self.dropout = Dropout(dropout_rate)

    def call(self, x, enc_output, training, look_ahead_mask, padding_mask):
        """Forward pass of Decoder."""
        x = self.embedding(x)  # (batch_size, target_seq_len, d_model)
        x *= tf.math.sqrt(tf.cast(self.d_model, x.dtype))

        sliced_pos_encoding = self._get_sliced_positional_encoding(x)
        x = tf.cast(x, dtype=tf.float32)
        x += sliced_pos_encoding

        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x = self.dec_layers[i](
                x, enc_output, training=training, look_ahead_mask=look_ahead_mask, padding_mask=padding_mask
            )

        return x

    def _get_sliced_positional_encoding(self, x):
        """Get positional encoding sliced to the right length."""
        return self.pos_encoding[:, :tf.shape(x)[1], :]


class EncoderLayer(tf.keras.layers.Layer):
    """Transformer Encoder Layer."""

    def __init__(self, d_model, num_heads, d_feedforward, dropout_rate=0.1):
        super(EncoderLayer, self).__init__()
        self.mha = MultiHeadAttention(key_dim=d_model, num_heads=num_heads)
        self.ffn = tf.keras.Sequential(
            [Dense(d_feedforward, activation="relu"), Dense(d_model)]
        )
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(dropout_rate)
        self.dropout2 = Dropout(dropout_rate)

    def call(self, x, training, mask):
        """Forward pass of EncoderLayer."""
        attn_output = self.mha(x, x, x, attention_mask=mask)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)

        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(out1 + ffn_output)

        return out2


class DecoderLayer(tf.keras.layers.Layer):
    """Transformer Decoder Layer."""

    def __init__(self, d_model, num_heads, d_feedforward, dropout_rate=0.1):
        super(DecoderLayer, self).__init__()
        self.mha1 = MultiHeadAttention(key_dim=d_model, num_heads=num_heads)
        self.mha2 = MultiHeadAttention(key_dim=d_model, num_heads=num_heads)

        self.ffn = tf.keras.Sequential(
            [Dense(d_feedforward, activation="relu"), Dense(d_model)]
        )
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.layernorm3 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(dropout_rate)
        self.dropout2 = Dropout(dropout_rate)
        self.dropout3 = Dropout(dropout_rate)

    def call(self, x, enc_output, training, look_ahead_mask, padding_mask):
        """Forward pass of DecoderLayer."""
        attn1 = self.mha1(x, x, x, attention_mask=look_ahead_mask)
        attn1 = self.dropout1(attn1, training=training)
        out1 = self.layernorm1(attn1 + x)

        attn2 = self.mha2(
            out1, enc_output, enc_output, attention_mask=padding_mask
        )
        attn2 = self.dropout2(attn2, training=training)
        out2 = self.layernorm2(attn2 + out1)

        ffn_output = self.ffn(out2)
        ffn_output = self.dropout3(ffn_output, training=training)
        out3 = self.layernorm3(ffn_output + out2)

        return out3


if __name__ == "__main__":
    # Define Transformer parameters
    num_layers = 4
    d_model = 128
    num_heads = 8
    d_feedforward = 512
    input_vocab_size = 150  # Increased for music tokens
    target_vocab_size = 150  # Increased for music tokens
    dropout_rate = 0.1
    pe_input = 512
    pe_target = 512

    # Instantiate the Transformer model
    transformer_model = Transformer(
        num_layers,
        d_model,
        num_heads,
        d_feedforward,
        input_vocab_size,
        target_vocab_size,
        pe_input,
        pe_target,
        dropout_rate,
    )

    # Dummy input shapes for encoder and decoder
    dummy_inp = tf.random.uniform(
        (1, 10), dtype=tf.int64, minval=0, maxval=input_vocab_size
    )
    dummy_tar = tf.random.uniform(
        (1, 10), dtype=tf.int64, minval=0, maxval=target_vocab_size
    )

    # Build the model using dummy input
    transformer_model(
        dummy_inp,
        dummy_tar,
        training=False,
        enc_padding_mask=None,
        look_ahead_mask=None,
        dec_padding_mask=None,
    )

    # Display the model summary
    transformer_model.summary()