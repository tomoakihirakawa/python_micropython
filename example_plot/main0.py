'''
時間をかけないと身につきません．
自分の手で打ち込んでください．
'''

def linspace(s,e,n):
    d = (e-s)/(n-1)
    return [s+d*i for i in range(n)]

X = linspace(0,10,10)
print(X)