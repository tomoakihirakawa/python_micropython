# 使い方

関節の角度.nbで魚の関節の時間変化を計算し，json形式で出力する．
jsonの内容は，check_data.pyで確認できる．

![each_angle.png](./each_angle.png)
![time_to_dataindex.png](./time_to_dataindex.png)
![each_angle_signal.png](./each_angle_signal.png)

move_servo.pyを実行すれば，
jsonファイルを読み込みその内容に従うよう
サーボモーターが駆動する

ただし，
実際にサーボモーターを動かすためには，

* servomotorパッケージ
* PCA9685パッケージ


をpython_sharedからこのディレクトリにコピーしておくこと．

