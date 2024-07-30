import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

# モデルを読み込む
model = load_model('my_model.keras')

# Softmax関数を適用して予測を出力
probability_model = tf.keras.Sequential([
    model,
    tf.keras.layers.Softmax()
])

# 画像の読み込みと前処理
def preprocess_image(image_path, save_preprocessed=False):
    # 画像を読み込む
    image = Image.open(image_path).convert('L')
    # コントラストの調整
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(10.0)
    # 画像を反転して背景を黒、数字を白にする
    image = ImageOps.invert(image)
    # 画像を28x28ピクセルにリサイズ
    image = image.resize((28, 28))
    # 画像をnumpy配列に変換
    image_array = np.array(image)
    # 画像の正規化
    image_array = image_array / 255.0
    # 画像の形状を変更
    image_array = np.expand_dims(image_array, axis=0)
    
    # 前処理後の画像を保存
    if save_preprocessed:
        preprocessed_image = Image.fromarray((image_array[0] * 255).astype(np.uint8))
        preprocessed_image.save(os.path.splitext(image_path)[0] + '_preprocessed.png')
    
    return image_array

# ローカルな"number.png"を読み込んで予測を行う
for i in range(1, 10):
    # ファイルパスを文字列に変換
    file = "./handwritten_numbers" + '/num' + str(i) + '.png'    
    image_array = preprocess_image(file, save_preprocessed=True)

    # 予測を行う
    predictions = probability_model.predict(image_array)
    predicted_digit = np.argmax(predictions)

    print(f'path: {file}')
    print(f'予測された数字: {predicted_digit}')
