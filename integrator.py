
class integratorMultiple:
    def __init__(self, dimIN):
        self.dim = dimIN
        self.t = []
        self.values = []
        self.integral = [0.]*dimIN
        self.integrals = [self.integral]
        self.double_integral = [0]*dimIN
        self.double_integrals = [self.integral]
        self.start_integrate = False

    def add(self, t, xyz):
        # if len(xyz) is not self.dim:
        #     print('エラー：addしようと与えられたベクトルは，現在積分しているベクトルと次元が違う．')
        #     raise ValueError

        self.values.append(xyz)
        self.t.append(t)

        if self.start_integrate:
            dt = self.t[-1] - self.t[-2]
            for i in range(self.dim):
                self.integral[i] += (xyz[i] + self.values[-2][i])*dt/2.

            self.integrals.append(self.integral.copy())

            for i in range(self.dim):
                self.double_integral[i] += (self.integral[i] +
                                            self.integrals[-2][i])*dt/2.

            self.double_integrals.append(self.double_integral.copy())

        self.start_integrate = True


class integrator:
    def __init__(self):
        self.t = []
        self.values = []
        self.integral = 0.
        self.integrals = [self.integral]
        self.double_integral = 0.
        self.double_integrals = [self.integral]

    def add(self, t, x):
        self.values.append(x)
        self.t.append(t)

        if len(self.t) > 1:
            dt = self.t[-1] - self.t[-2]
            dx = self.values[-1] + self.values[-2]
            self.integral += dx*dt/2.
            self.integrals.append(self.integral.copy())
            dx = self.integrals[-1] + self.integrals[-2]

            self.double_integral[i] += dx*dt/2.
            self.double_integrals.append(self.double_integral.copy())
