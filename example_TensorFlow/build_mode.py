# pip install tensorflow matplotlib numpy pillow

import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np

# MNISTデータセットのロード
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# データの正規化
x_train, x_test = x_train / 255.0, x_test / 255.0

# モデルの構築
model = models.Sequential([
    layers.Flatten(input_shape=(28, 28)),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(10)
])

# モデルのコンパイル
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])

# モデルのトレーニング
model.fit(x_train, y_train, epochs=5)

# モデルの評価
model.evaluate(x_test, y_test, verbose=2)

# Softmax関数を適用して予測を出力
probability_model = tf.keras.Sequential([
    model,
    tf.keras.layers.Softmax()
])

# モデルを保存
model.save('my_model.keras')
