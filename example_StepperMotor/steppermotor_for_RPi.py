'''DOC_EXTRACT 0_0_0_steppermotor_for_raspi5

# ステッピングモーターの制御

<img src="sample_linear_guide.gif" style="width: 600px; display: block; margin: 0 auto;">

ステッピングモーターは１パルスごとに一定の角度だけ回転する．
このStepperMotorクラスでは，StepperMotor.runメソッドを定義し，その中でモーターを制御する．

クラスの初期化は以下のように行う．

```python
motor = StepperMotor(dir_pin=12, step_pin=13, dxdq=8, pulse_per_rev=6400)
```

`dxdq`[mm]はモーターの規格で決まるものではなく，リニアガイドのピッチ[mm]である．
`pulse_per_rev`もモーターの規格で決まるものではなく，モータードライバの設定による．

```python
thread_process_loop = threading.Thread(target=motor.run, args=(position_func, stop_condition)) #スレッドを作成と同時に実行する関数をわたす
thread_process_loop.start() #スレッドを開始する
thread_process_loop.join() #実行したスレッドが終了するまで待つ
```

StepperMotor.runには，position_funcとstop_conditionという２つの関数を引数として渡す．

* position_funcは，リニアガイドにおける台の位置が時間とともにどのように移動するかを定義する関数である．
* stop_conditionは，runを終了するかどうかを判断する関数である．

run内では，run開始とともに，time.perf_counter()を使って，経過時間を計測しており，その時間をposition_funcに渡している．

例：

以下の例では，振幅A=2[mm]，周期T=0.1[s]の正弦波に乗って移動する台の位置を定義している．とても早いが問題なく動作した．

```python
A = 2
T = .1
def position_func(t):
    return A * math.sin(2 * math.pi / T * t) * (1-math.exp(-t))
```

以下のように，振幅A=30[mm]，周期T=0.5[s]の正弦波に乗って移動する台の位置を定義しても問題なく動作する．

```python
A = 30
T = .5
def position_func(t):
    return A * math.sin(2 * math.pi / T * t) * (1-math.exp(-t))
```

ただ，振幅A=40[mm]，周期T=0.5[s]だと，モーターが追いつかないようだ．

'''

from lib.steppermotor import StepperMotor
import math
import threading

if __name__ == "__main__":

    motor = StepperMotor(dir_pin=12, step_pin=13, dxdq=8, pulse_per_rev=6400)

    A = 10
    T = 1.
    def position_func(t):
        return A * math.sin(2 * math.pi / T * t) * (1-math.exp(-t))

    def stop_condition(t):
        return t > 10

    thread_process_loop = threading.Thread(target=motor.run, args=(position_func, stop_condition)) #スレッドを作成と同時に実行する関数をわたす
    thread_process_loop.start() #スレッドを開始する
    thread_process_loop.join() #実行したスレッドが終了するまで待つ