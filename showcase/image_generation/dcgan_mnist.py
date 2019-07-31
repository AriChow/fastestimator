from fastestimator.estimator.estimator import Estimator
from fastestimator.pipeline.pipeline import Pipeline
from fastestimator.pipeline.preprocess import TensorPreprocess
from tensorflow.keras import layers
from fastestimator.network.loss import Loss
from fastestimator.network.network import Network
from fastestimator.network.model import ModelOp, build
import tensorflow as tf
import numpy as np

class g_loss(Loss):
    def __init__(self):
        self.cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    def calculate_loss(self, batch, prediction):
        return self.cross_entropy(tf.ones_like(prediction["pred_fake"]), prediction["pred_fake"])

class d_loss(Loss):
    def __init__(self):
        self.cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    def calculate_loss(self, batch, prediction):
        real_loss = self.cross_entropy(tf.ones_like(prediction["pred_true"]), prediction["pred_true"])
        fake_loss = self.cross_entropy(tf.zeros_like(prediction["pred_fake"]), prediction["pred_fake"])
        total_loss = real_loss + fake_loss
        return total_loss

def make_generator_model():
    model = tf.keras.Sequential()
    model.add(layers.Dense(7*7*256, use_bias=False, input_shape=(100,)))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Reshape((7, 7, 256)))
    assert model.output_shape == (None, 7, 7, 256) # Note: None is the batch size
    model.add(layers.Conv2DTranspose(128, (5, 5), strides=(1, 1), padding='same', use_bias=False))
    assert model.output_shape == (None, 7, 7, 128)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False))
    assert model.output_shape == (None, 14, 14, 64)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    assert model.output_shape == (None, 28, 28, 1)
    return model

def make_discriminator_model():
    model = tf.keras.Sequential()
    model.add(layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same', input_shape=[28, 28, 1]))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
    model.add(layers.Flatten())
    model.add(layers.Dense(1))
    return model

class Myrescale(TensorPreprocess):
    def forward(self, data):
        data = tf.cast(data, tf.float32)
        data = (data - 127.5) / 127.5
        return data

def get_estimator():
    #prepare data
    (x_train, y_train), (x_eval, y_eval) = tf.keras.datasets.mnist.load_data()
    data = {"train":  {"x": np.expand_dims(x_train, -1)},  "eval": {"x": np.expand_dims(x_eval, -1)}}
    pipeline = Pipeline(batch_size=32,
                        data=data,
                        ops=Myrescale(inputs="x", outputs="x"))
    #prepare model
    g = build(keras_model=make_generator_model(), loss=g_loss(), optimizer=tf.optimizers.Adam(1e-4))
    d = build(keras_model=make_discriminator_model(), loss=d_loss(), optimizer=tf.optimizers.Adam(1e-4))
    network = Network(ops= [ModelOp(inputs=lambda: tf.random.normal([32, 100]), model=g), ModelOp(model=d, outputs="pred_fake"),
                            ModelOp(inputs="x", model=d, outputs="pred_true")])
    #prepare estimator
    estimator = Estimator(network= network,
                          pipeline=pipeline,
                          epochs= 2)
    return estimator