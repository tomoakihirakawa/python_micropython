

class evalClass():
    def __init__(self):
        print("initialized")
        
    def total(self,lst):
        ret = 0.
        for x in lst:
            ret += x
        return ret
    
    def evaluate(self,jsn):
        for key, value in jsn.items():
            try:
                return eval("self."+key+"("+str(value)+")")
            except:
                pass

e = evalClass()
a=e.evaluate({"total":[1,2,3]})
print(a)
    