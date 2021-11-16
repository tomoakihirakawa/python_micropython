#!/usr/bin/python
#システムマネジメントバスを操作るためのモジュールをインポート
import smbus
# バスの番号（デフォルトでは１がi2cのようだ）．
# ラズパイでは，/boot/config.txtを書き換えることで，i2cバスの数を増やすことができる．
bus_num = 1
# バスオブジェクトを作成．このオブジェクトを通してマルチプレクサのチャンネルを変更する．
bus = smbus.SMBus(bus_num)
# マルチプレクサへのチャンネル（１６進数）
ch = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80] #channel numbers

# マルチプレクサに接続している，センサーの数
num_sensor = 3

# マルチプレクサのアドレス
address = 0x70 #multiplexer's address

# 圧力センサーを操作するためのモジュールをインポート
import ms5837
# 時間を操作するためのモジュールをインポート
import time

# センサーオブジェクトを格納する配列
sensor = []

# センサーを初期化して，センサーオブジェクト用の配列に格納
for num in range(num_sensor):
        bus.write_byte_data(0x70,0x40,ch[num]) #0x04 is the register for switching channels
        sensor.append(ms5837.MS5837_02BA(bus_num))
        if not sensor[num].init():
                print("Sensor could not be initialized")
                exit(1)
        if not sensor[num].read():
                print("Sensor read failed!")
                exit(1)

######################################
dir_name = "/home/pi/Desktop/karasawa/"
f_name = raw_input("Enter file name : "+dir_name)
f = open(dir_name+f_name,'w')
beg_t = time.time()
elp_t = 0
end_t = 10
counter = 0
######################################

# チャンネル変る，センサーを読む，データを書き込む，を繰り返す
while (elp_t < end_t):
        counter+=1.
        for num in range(num_sensor):
                # switch channels
                bus.write_byte_data(0x70,0x40,ch[num])
                if sensor[num].read(5):
                        elp_t = time.time() - beg_t
                        p = sensor[num].pressure()
                        temp = sensor[num].temperature()
                        print("%0.3f, %0.3f, %0.3f") % (elp_t, p, temp)
                        f.write("%0.3f, %0.3f, %0.3f, " % (elp_t, p, temp) )
                else:
                        print("Sensor read failed!")
                        exit(1)
        f.write("\n")

print("*********************************")
print("The number of data : %d") % counter
tmp = end_t/counter
print("Approximated dt : %0.3f") % tmp
print("File name : %s") % dir_name + f_name
print("*********************************")
f.close()
