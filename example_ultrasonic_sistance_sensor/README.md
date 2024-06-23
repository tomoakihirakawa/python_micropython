# Contents

- [🤖HC-SR04 or JSN-SR04 Ultrasonic Sensor with Raspberry Pi 5](#🤖HC-SR04-or-JSN-SR04-Ultrasonic-Sensor-with-Raspberry-Pi-5)


---
# 🤖HC-SR04 or JSN-SR04 Ultrasonic Sensor with Raspberry Pi 5 

このPythonコードは，Raspberry Pi 5で超音波センサーを使用するためのものです．
GPIOを利用するためのライブラリとして，さまざまな選択肢がありますが，Raspberry Pi 5ではまだサポートされていないため，gpiodを使用しています．

まず，gpioinfoコマンドを使用して，各ピンがどのGPIOチップに接続されているかを確認し，適切なチップを設定します．初めに5番ピンと6番ピンを使おうとしましたが，LEDの点滅には利用できたものの，この超音波センサーのトリガーとエコーとしては利用できませんでした．そのため，23番ピンと22番ピンを使用しています．

このコードでは，超音波センサーのトリガーピンを最初にゼロにセットします．次に，10マイクロ秒のパルスをトリガーピンに送ります．エコーピンがパルスを受信するまでの時間を測定し，その時間をもとに距離を計算します．具体的には，音速を34300 cm/sと仮定して，測定した時間に基づいて距離を求めます．


[./HC-SR04.py#L1](./HC-SR04.py#L1)


---
