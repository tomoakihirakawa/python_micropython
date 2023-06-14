from time import sleep
import json

data = {}
data['TimeCapsule'] = "Tomoaki813;"
data['ce317_gakusei'] = "dobokuday1118"

# 　writeとreadを同じフォルダで実行しようとするとエラーがでる-> closeしていないから
outputfile = open('ssid_pwd.json', 'w')
json.dump(data, outputfile)
outputfile.close()

try:
    inputfile = open('ssid_pwd.json', encoding='utf-8')
    data = json.load(inputfile)
    print(data)
    for a, b in data.items():
        print(a, b)
except IOError:
    print("files is not found")
