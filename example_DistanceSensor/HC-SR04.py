'''DOC_EXTRACT

# HC-SR04 or JSN-SR04 Ultrasonic Sensor with Raspberry Pi 5

このPythonコードは，Raspberry Pi 5で超音波センサーを使用するためのものです．
GPIOを利用するためのライブラリとして，さまざまな選択肢がありますが，Raspberry Pi 5ではまだサポートされていないため，gpiodを使用しています．

まず，gpioinfoコマンドを使用して，各ピンがどのGPIOチップに接続されているかを確認し，適切なチップを設定します．初めに5番ピンと6番ピンを使おうとしましたが，LEDの点滅には利用できたものの，この超音波センサーのトリガーとエコーとしては利用できませんでした．そのため，23番ピンと22番ピンを使用しています．

このコードでは，超音波センサーのトリガーピンを最初にゼロにセットします．次に，10マイクロ秒のパルスをトリガーピンに送ります．エコーピンがパルスを受信するまでの時間を測定し，その時間をもとに距離を計算します．具体的には，音速を34300 cm/sと仮定して，測定した時間に基づいて距離を求めます．

'''

import gpiod
import time

# Setup GPIO chip and lines
try:
    chip = gpiod.Chip('gpiochip4')  # Using gpiochip0
    trig = chip.get_line(23)        # BT_TXD line as output for trigger
    echo = chip.get_line(22)        # BT_RXD line as input for echo

    # Requesting lines
    trig.request(consumer='measure_distance', type=gpiod.LINE_REQ_DIR_OUT)
    echo.request(consumer='measure_distance', type=gpiod.LINE_REQ_DIR_IN)
except Exception as e:
    print(f"Error setting up GPIO: {e}")
    exit(1)

def measure_distance():
    try:
        # Ensure the trigger pin is set low
        trig.set_value(0)
        time.sleep(0.004)  # 2ms delay to ensure sensor is settled
        # Send a 10us pulse to trigger the sensor        
        
        trig.set_value(1)
        time.sleep(0.00001)  # 10us delay
        trig.set_value(0)

        # Wait for the echo start
        while echo.get_value() == 0:
            start = time.time()

        # Wait for the echo end
        while echo.get_value() == 1:
            stop = time.time()

        # Calculate the duration of the pulse
        # Calculate the distance (speed of sound is 34300 cm/s)
        return ((stop - start) * 34300)*0.5
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return None

dist = 0
a=0.1

try:
    while True:
        dist = measure_distance()
        # print "*" for each cm
        print("*" * int(dist))
        if dist is not None:
            print(f"Distance: {dist} cm")
        time.sleep(0.02)  # Delay before next measurement

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    try:
        trig.release()
        echo.release()
        chip.close()
    except Exception as e:
        print(f"Error releasing GPIO resources: {e}")
