import numpy as np
import tensorflow as tf
import time
import os
import h5py


def scaled_dot_product_attention(q, k, v, mask):
    """Calculate the attention weights.
    q, k, v must have matching leading dimensions.
    k, v must have matching penultimate dimension, i.e.: seq_len_k = seq_len_v.
    The mask has different shapes depending on its type(padding or look ahead) 
    but it must be broadcastable for addition.
    
    Args:
        q: query shape == (..., seq_len_q, depth)
        k: key shape == (..., seq_len_k, depth)
        v: value shape == (..., seq_len_v, depth_v)
        mask: Float tensor with shape broadcastable 
            to (..., seq_len_q, seq_len_k). Defaults to None.
        
    Returns:
        output, attention_weights
    """

    matmul_qk = tf.matmul(q, k, transpose_b=True)  # (..., seq_len_q, seq_len_k)

    # scale matmul_qk
    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

    # add the mask to the scaled tensor.
    if mask is not None:
        scaled_attention_logits += mask * -1e9

    # softmax is normalized on the last axis (seq_len_k) so that the scores
    # add up to 1.
    attention_weights = tf.nn.softmax(
        scaled_attention_logits, axis=-1
    )  # (..., seq_len_q, seq_len_k)

    output = tf.matmul(attention_weights, v)  # (..., seq_len_q, depth_v)

    return output, attention_weights


class MultiHeadAttention(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model

        assert d_model % self.num_heads == 0

        self.depth = d_model // self.num_heads

        self.wq = tf.keras.layers.Dense(d_model)
        self.wk = tf.keras.layers.Dense(d_model)
        self.wv = tf.keras.layers.Dense(d_model)

        self.dense = tf.keras.layers.Dense(d_model)

    def split_heads(self, x, batch_size):
        """Split the last dimension into (num_heads, depth).
        Transpose the result such that the shape is (batch_size, num_heads, seq_len, depth)
        """
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, v, k, q, mask):
        batch_size = tf.shape(q)[0]

        q = self.wq(q)  # (batch_size, seq_len, d_model)
        k = self.wk(k)  # (batch_size, seq_len, d_model)
        v = self.wv(v)  # (batch_size, seq_len, d_model)

        q = self.split_heads(q, batch_size)  # (batch_size, num_heads, seq_len_q, depth)
        k = self.split_heads(k, batch_size)  # (batch_size, num_heads, seq_len_k, depth)
        v = self.split_heads(v, batch_size)  # (batch_size, num_heads, seq_len_v, depth)

        # scaled_attention.shape == (batch_size, num_heads, seq_len_q, depth)
        # attention_weights.shape == (batch_size, num_heads, seq_len_q, seq_len_k)
        scaled_attention, attention_weights = scaled_dot_product_attention(
            q, k, v, mask
        )

        scaled_attention = tf.transpose(
            scaled_attention, perm=[0, 2, 1, 3]
        )  # (batch_size, seq_len_q, num_heads, depth)

        concat_attention = tf.reshape(
            scaled_attention, (batch_size, -1, self.d_model)
        )  # (batch_size, seq_len_q, d_model)

        output = self.dense(concat_attention)  # (batch_size, seq_len_q, d_model)

        return output, attention_weights


def point_wise_feed_forward_network(d_model, dff):
    return tf.keras.Sequential(
        [
            tf.keras.layers.Dense(dff, activation="relu"),  # (batch_size, seq_len, dff)
            tf.keras.layers.Dense(d_model),  # (batch_size, seq_len, d_model)
        ]
    )


class EncoderLayer(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads, dff, rate=0.1):
        super(EncoderLayer, self).__init__()

        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = point_wise_feed_forward_network(d_model, dff)

        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)

        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)

    def call(self, x, training, mask):
        attn_output, _ = self.mha(x, x, x, mask)  # (batch_size, input_seq_len, d_model)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)  # (batch_size, input_seq_len, d_model)

        ffn_output = self.ffn(out1)  # (batch_size, input_seq_len, d_model)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(
            out1 + ffn_output
        )  # (batch_size, input_seq_len, d_model)

        return out2


class Encoder(tf.keras.layers.Layer):
    def __init__(
        self,
        num_layers,
        d_model,
        num_heads,
        dff,
        input_vocab_size,
        maximum_position_encoding,
        rate=0.1,
    ):
        super(Encoder, self).__init__()

        self.d_model = d_model
        self.num_layers = num_layers

        self.embedding = tf.keras.layers.Embedding(input_vocab_size, d_model)
        self.pos_encoding = self.add_variable(
            "position_embedding", shape=[1, maximum_position_encoding, self.d_model]
        )

        self.enc_layers = [
            EncoderLayer(d_model, num_heads, dff, rate) for _ in range(num_layers)
        ]

        self.dropout = tf.keras.layers.Dropout(rate)

    def call(self, x, training, mask):
        x = self.embedding(x)  # (batch_size, input_seq_len, d_model)
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
        x += self.pos_encoding
        x = self.dropout(x, training=training)
        for i in range(self.num_layers):
            x = self.enc_layers[i](x, training, mask)

        return x  # (batch_size, input_seq_len, d_model)


class Model(tf.keras.Model):
    def __init__(self):
        super(Model, self).__init__()

        self.num_layers = 2
        self.d_model = 8
        self.dff = 8
        self.num_heads = 1
        self.input_vocab_size = 1600
        self.dropout_rate = 0.1
        self.maximum_position_encoding = 7500

        self.encoder = Encoder(
            self.num_layers,
            self.d_model,
            self.num_heads,
            self.dff,
            self.input_vocab_size,
            self.maximum_position_encoding,
            self.dropout_rate,
        )

    def __call__(self, x, idxnon, pos, training, mask, mask_cross):
        x = self.encoder(x, training, mask)
        gen = x[:, :2500]  # (b, 2500, model)
        gen = tf.reshape(gen, [-1, 5, 50, 10, self.d_model])  # (b, 5, 50, 10, model)
        gen = tf.gather(
            gen, tf.expand_dims(idxnon, -1), batch_dims=1
        )  # (b, 1, 50, 10, model)
        gen = tf.squeeze(gen, axis=1)  # (b, 50, 10, model)
        gen = tf.reduce_max(gen, axis=2)  # (b, 50, model)

        non = x[:, 6500:]  # (b, 1000, model)
        non = tf.gather(non, tf.expand_dims(pos, -1), batch_dims=1)  # (b, 1, model)

        cross = tf.math.reduce_sum(gen * non, axis=-1)
        cross = cross + mask_cross * -1e9
        # cross = tf.nn.softmax(cross)
        return cross


EPOCHS = 1000

BUFFER_SIZE = 20000
BATCH_SIZE = 8


def create_masks(x, idxnon):
    mask1 = tf.cast(x == 0, tf.float32)
    mask1 = mask1[:, tf.newaxis, tf.newaxis, :]
    mask2 = x[:, :2500]
    mask2 = tf.reshape(mask2, [-1, 5, 50, 10])  # (b, 5, 50, 10)
    mask2 = tf.gather(mask2, tf.expand_dims(idxnon, -1), batch_dims=1)  # (b, 1, 50, 10)
    mask2 = tf.squeeze(mask2, axis=1)  # (b, 50, 10)
    mask2 = mask2[:, :, 0]  # (b, 50)
    mask_del = tf.cast(mask2 == 0, tf.float32)
    return mask1, mask_del


class SygusNetwork:
    def __init__(self):
        self.model = Model()

        self.optimizer = tf.keras.optimizers.Adam()
        self.loss_object = tf.keras.losses.CategoricalCrossentropy(
            from_logits=True, reduction=tf.keras.losses.Reduction.NONE
        )

        self.train_loss = tf.keras.metrics.Mean(name="train_loss")
        self.train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(
            name="train_accuracy"
        )

        self.checkpoint_path = "./train"
        self.ckpt = tf.train.Checkpoint(
            transformer=self.model, optimizer=self.optimizer
        )
        self.ckpt_manager = tf.train.CheckpointManager(
            self.ckpt, self.checkpoint_path, max_to_keep=5
        )
        if self.ckpt_manager.latest_checkpoint:
            self.ckpt.restore(self.ckpt_manager.latest_checkpoint)
            print("Latest checkpoint restored!!")

    def loss_function(self, real, pred):
        real = tf.one_hot(real, 50, dtype=tf.float32)
        loss_ = self.loss_object(real, pred)
        return tf.reduce_mean(loss_)

    @tf.function(
        input_signature=[
            tf.TensorSpec(shape=(None, 7500), dtype=tf.int32),
            tf.TensorSpec(shape=(None,), dtype=tf.int32),
            tf.TensorSpec(shape=(None,), dtype=tf.int32),
            tf.TensorSpec(shape=(None,), dtype=tf.int32),
        ]
    )
    def train_step(self, x, idxnon, pos, idxrule):
        mask1, mask_del = create_masks(x, idxnon)

        with tf.GradientTape() as tape:
            predictions = self.model(x, idxnon, pos, True, mask1, mask_del)
            loss = self.loss_function(idxrule, predictions)

        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

        self.train_loss(loss)
        self.train_accuracy(idxrule, predictions)
        # tf.print(idxrule, summarize=-1)

    def loaddata(self):
        traindata = h5py.File("train.h5", "r")
        traindata = (
            traindata["seq"][()],
            traindata["idxnon"][()],
            traindata["pos"][()],
            traindata["idxrule"][()],
        )
        # traindata = (
        #     traindata["seq"][:12],
        #     traindata["idxnon"][:12],
        #     traindata["pos"][:12],
        #     traindata["idxrule"][:12],
        # )
        traindata = tf.data.Dataset.from_tensor_slices(traindata)
        self.traindata = traindata.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE)

    def train(self):
        for epoch in range(EPOCHS):
            start = time.time()

            self.train_loss.reset_states()
            self.train_accuracy.reset_states()

            # inp -> portuguese, tar -> english
            for (batch, (x, idxnon, pos, idxrule)) in enumerate(self.traindata):
                self.train_step(x, idxnon, pos, idxrule)

                if batch % 1 == 0:
                    print(
                        "Epoch {} Batch {} Loss {:.4f} Accuracy {:.4f}".format(
                            epoch + 1,
                            batch,
                            self.train_loss.result(),
                            self.train_accuracy.result(),
                        )
                    )

            ckpt_save_path = self.ckpt_manager.save()
            print(
                "Saving checkpoint for epoch {} at {}".format(epoch + 1, ckpt_save_path)
            )

            print(
                "Epoch {} Loss {:.4f} Accuracy {:.4f}".format(
                    epoch + 1, self.train_loss.result(), self.train_accuracy.result()
                )
            )

            print("Time taken for 1 epoch: {} secs\n".format(time.time() - start))


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    network = SygusNetwork()
    network.loaddata()
    network.train()
