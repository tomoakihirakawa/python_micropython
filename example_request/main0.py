import requests
import json
import matplotlib.pyplot as plt


resp = requests.get("https://docs.micropython.org/en/latest/develop/qstr.html")
text = resp.text
print(text)
#dict = json.loads(text)         
#print(resp.text)

# outF = open("requestme", "w")
# outF.write("{")
# for i in range(1):
#     # write line to output file
#     outF.write("\"x\":[1,2,3,4],")
#     outF.write("\n")  
#     outF.write("\"y\":[1,2,3,4],")  
#     outF.write("\n")
    
# outF.write("}")
# outF.close()

# for i in range(10):
#     plt.title(i)
#     plt.plot(dict["x"],dict["y"])
#     plt.draw()
#     plt.pause(0.1)
#     plt.clf()

