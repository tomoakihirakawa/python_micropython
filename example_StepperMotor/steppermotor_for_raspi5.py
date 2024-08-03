'''DOC_EXTRACT 0_0_0_steppermotor_for_raspi5

# `StepperMotor` クラス

このクラスはRaspberry Piとgpiodライブラリを使用してステッピングモーターを制御する．クラスの主な機能は以下の通りである：

- **コンストラクタ (`__init__` メソッド)**: GPIOピンの初期設定を行い，方向ピンとステップピンを初期化する．
- **`start` メソッド**: モーターの初期処理を行う．
- **`dir` メソッド**: モーターの回転方向を設定または取得する．
- **`freq` メソッド**: ステップ周波数を設定または取得する．
- **`set_step_frequency` メソッド**: 指定された周波数でステップパルスを生成する．
- **`accel` メソッド**: 周波数を変更してモーターを加速または減速する．

## `sinOmega1` 関数

この関数は，モーターの周波数をサイン波状に変更するためのスレッド関数である．周波数をサイン波状に変更することで，モーターの回転速度が滑らかに変化する．

## スレッドの説明

このスクリプトでは，Pythonの`threading`モジュールを使用して並行処理を実現している．スレッドを使用することで，モーターの周波数制御をバックグラウンドで実行しつつ，メインプログラムが他のタスクを処理できるようになる．

- **`threading.Thread` クラス**: 新しいスレッドを作成するために使用される．
- **`start` メソッド**: 新しいスレッドでターゲット関数を実行する．

## 使用方法

1. スクリプトを実行すると，`StepperMotor` クラスのインスタンスが作成され，モーターの初期設定が行われる．
2. `sinOmega1` 関数が新しいスレッドで実行され，モーターの周波数をサイン波状に変更する．

このスクリプトは，ステッピングモーターのスムーズな回転制御に役立つ．モーターの動作を微調整するには，スクリプト内のパラメータ（例えば，周波数や振幅）を変更することができる．

## 実行環境の注意点

1. gpiozeroライブラリがインストールされていることを確認する．
2. GPIOチップ番号とピン番号は，ハードウェア構成に応じて調整する．

これにより，Raspberry Piを使用したステッピングモーターの制御が効率的に行えるようになる．
'''

from gpiozero import OutputDevice
from time import sleep, time_ns
import threading
import math

class StepperMotor:
    """
    ステッピングモーターを制御するクラス
    Raspberry Piとgpiozeroライブラリを使用してGPIOピンを制御する．
    """
    def __init__(self, dir_pin, step_pin, freq=0):
        """
        コンストラクタ．ステッピングモーターのパラメータを初期化する．

        :param dir_pin: 方向ピンのGPIOピン番号．
        :param step_pin: ステップピンのGPIOピン番号．
        :param freq: ステップ周波数．
        """
        self.FREQ = freq
        self.Pin_dir = OutputDevice(dir_pin)
        self.Pin_step = OutputDevice(step_pin)
        self.DIR = 1
        self.dir(self.DIR)  # 初期方向を設定
        print("freq ", self.FREQ)
        print("Pin_dir ", self.Pin_dir)
        print("Pin_step ", self.Pin_step)

    def start(self):
        """
        ステッピングモーターの初期処理を行う．
        """
        sleep(0.0005)

    def dir(self, dir_IN=None):
        """
        モーターの回転方向を設定または取得する．

        :param dir_IN: 設定する回転方向 (1 または 0)．
        :return: 現在の回転方向．
        """
        if dir_IN is None:
            return self.DIR
        if self.DIR != dir_IN:
            self.DIR = dir_IN
            self.Pin_dir.value = dir_IN
        return self.DIR

    def freq(self, freq_IN=None):
        """
        ステップ周波数を設定または取得する．

        :param freq_IN: 設定する周波数 (Hz)．
        :return: 現在の周波数．
        """
        if freq_IN is None:
            return self.FREQ
        else:
            self.FREQ = freq_IN
            if self.FREQ < 0:
                self.dir(0)
                self.set_step_frequency(-self.FREQ)
            else:
                self.dir(1)
                self.set_step_frequency(self.FREQ)
        return self.FREQ

    def set_step_frequency(self, frequency):
        """
        指定された周波数でステップパルスを生成する．

        :param frequency: 周波数 (Hz)．
        """
        period = 1.0 / frequency
        while True:
            self.Pin_step.on()
            sleep(period / 2)
            self.Pin_step.off()
            sleep(period / 2)

    def accel(self, w):
        """
        周波数を変更してモーターを加速または減速する．

        :param w: 変更する周波数の量．
        """
        print(w)
        self.freq(self.FREQ + w)

def sinOmega1(motor):
    """
    モーターの周波数をサイン波状に変更する．

    :param motor: ステッピングモーターオブジェクト．
    """
    s = time_ns()
    T = 2.0 * math.pi  # 周期
    A = 3.0 * 160.0   # 振幅（分解能を1/10に減らす）
    while True:
        t = (time_ns() - s) * 1e-9
        tmp = round(A * math.sin(2.0 * math.pi * t / T))
        print(tmp)
        motor.freq(tmp)

if __name__ == "__main__":
    motor = StepperMotor(dir_pin=12, step_pin=13)  # StepperMotorのインスタンスを作成する．
    motor.start()  # モーターを開始する．

    # スレッドを作成してsinOmega1関数を実行する．
    thread_process_loop = threading.Thread(target=sinOmega1, args=(motor,))
    thread_process_loop.start()
