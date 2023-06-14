class Person:
    __slots__ = ['firstname','lastname','h','w']
    def __init__(self, firstname, lastname,h,w):
        self.firstname = firstname
        self.lastname = lastname
        self.h = h/100
        self.w = w
        
    def BMI(self):
        return self.w/self.h**2
        
me = Person("tomoaki","hirakawa",180,65)
print(me.firstname)
print(me.lastname)
print(me.BMI())
