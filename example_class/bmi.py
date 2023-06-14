class Person:
    def __init__(self, namae, myouji, h, w):
        self.myouji = myouji
        self.namae = namae
        self.h = h
        self.w = w
    
    def bmi(self):
        return self.w/self.h/self.h


me = Person('a','b',177.,65)
print(me.h)
print(me.w)

print('------------------------')

group=[]
group.append(Person('suzuki','taro',177.,65))
group.append(Person('toyota','jiro',150.,55))
group.append(Person('honda','saburo',166.,45))
group.append(Person('subaru','siro',147.,25))

for g in group:
    print([g.namae,g.h,g.w,g.bmi()])