

|     |      | max freq for 12V      |                                             |
| --- | ---- | --------------------- | ------------------------------------------- |
| 1   | 200  | ~  1500 (Hz)=(step/s) | ~  1500(step/s)/200(step/rot)  = 7.5(rot/s) |
| 4   | 800  | ~  6000 (Hz)=(step/s) | ~  6000(step/s)/800(step/rot)  = 7.5(rot/s) |
| 8   | 1600 | ~ 12000 (Hz)=(step/s) | ~ 12000(step/s)/1600(step/rot) = 7.5(rot/s) |
| 16  | 3200 | ~ 24000 (Hz)=(step/s) | ~ 24000(step/s)/1600(step/rot) = 7.5(rot/s) |


1600(step/rot)の場合，W(Hz=step/s)/1600(step/rot) = W/1600 (rot/s)

一回転で進む距離，c(m/rot)=0.04(m/rot)?

*    V = c *    W / 1600  (m/s)
* dVdt = c * dWdt / 1600  (m/s^2)



# sin,cos振動

* 関数cos_wave((a,T,end_time))は，a*cos(2*pi*t/T)で


https://github.com/tomoakihirakawa/python_shared/blob/main/python_shared_lib/steppermotor/sloshing_test.mp4
