from numpy import quantile
from math import sin, cos, pi, radians,sqrt
from fundamental import *

def Power(d, n):
    return d**n


def Sqrt(d):
    return d**(1/2)


class fusion:

    def __init__(self, qIN=[1,0,0,0], inclination=-54):
        # 磁場の方向
        self.mc = cos(inclination/180*pi)
        self.ms = sin(inclination/180*pi)
        self.Q = Quaternion(qIN)
        self.dq = [0, 0, 0, 0]
        self.dqdt = [0, 0, 0, 0]
        self.A = [[0, 0, 0], [0, 0, 0]]
        self.M = [[0, 0, 0], [0, 0, 0]]

        # self.Q0 = Quaternion(qIN)
        # self.Q1 = Quaternion(qIN)
        # self.Q2 = Quaternion(qIN)

    # def estimateQ(self,q0,q1,w0,w1,w2,t0,t1,t2):
        
    #     self.estQ.set(q0*Power(t1 - t2,3)*w0 + q1*(t0 - t2)*(2*t0 - 2*t1 - Power(t1 - t2,2)*w1))/((t0 - t1)*(2*t0 - 2*t2 + (t0 - t1)*(t1 - t2)*w2))

    def __call__(self, A_IN, M_IN, W, dt):
        self.A[0] = Normalize(A_IN)
        self.M[0] = Normalize(M_IN)
        A = Times(Add(self.A[0], self.A[1]), 0.5)
        M = Times(Add(self.M[0], self.M[1]), 0.5)
        self.A[1] = self.A[0]
        self.M[1] = self.A[0]
        dq_w = self.Q.d_dt(W)
        self.Q.set(Add(self.Q(), Times(dq_w, dt)))
        for i in range(5):
            self.dq = self.dQ(A, M)
            self.Q.set(Add(self.Q(), self.dq))

        # normalization is necessary
        # print(['dq_w=', dq_w])
        # print(['dq_e=', dq_e])
        # dq = Times(self.Q.d_dt(W), dt)
        # W is current angular velocity
        # self.Q.set(Normalize(Add(self.Q(), dq)))
        # self.Q.set(Normalize(self.Q()))

        return self.Q()

    def update0(self, Ain, Min, W, dt, num=0):
        A = Normalize(Ain)
        M = Normalize(Min)

        if num > 0:
            for i in range(num):
                self.dq = self.dQ(A, M)
                self.Q.set(Add(self.Q(), self.dq))
        else:
            for i in range(30):
                self.dq = self.dQ(A, M)
                self.Q.set(Add(self.Q(), self.dq))
                if Norm(self.dq) < 10**-5:
                    break

        return self.Q.set(Normalize(self.Q()))
    
    def update1(self, Ain, Min, W, dt, num=0):
        self.A[0] = Normalize(Ain)
        self.M[0] = Normalize(Min)
        A = Normalize(Times(Add(self.A[0], self.A[1]), 0.5))
        M = Normalize(Times(Add(self.M[0], self.M[1]), 0.5))
        self.A[1] = self.A[0]
        self.M[1] = self.M[0]

        if num > 0:
            for i in range(num):
                self.dq = self.dQ(A, M)
                self.Q.set(Add(self.Q(), self.dq))
        else:
            for i in range(30):
                self.dq = self.dQ(A, M)
                self.Q.set(Add(self.Q(), self.dq))
                if Norm(self.dq) < 10**-5:
                    break

        return self.Q.set(Normalize(self.Q()))

    def update2(self, Ain, Min, W, dt, num=0):
        self.A[0] = Normalize(Ain)
        self.M[0] = Normalize(Min)
        alpha = 0.6
        self.A[1] = Normalize(Add(Times(self.A[0], alpha), Times(self.A[1],1. - alpha)))
        self.M[1] = Normalize(Add(Times(self.M[0], alpha), Times(self.M[1],1. - alpha)))        
        A = self.A[1]
        M = self.M[1]        

        if num > 0:
            for i in range(num):
                self.dq = self.dQ(A, M)
                self.Q.set(Add(self.Q(), self.dq))
        else:
            for i in range(20):
                self.dq = self.dQ(A, M)
                self.Q.set(Add(self.Q(), self.dq))
                if Norm(self.dq) < 10**-3:
                    break

        return self.Q.set(Normalize(self.Q()))

    def update00(self, A, M, W, dt, num=0):        
        self.dqdt[1] = self.Q.d_dt(W)
        self.Q.set((Add(self.Q(), Times(Add(self.dqdt[0],self.dqdt[1]),dt/2.))))
        self.dqdt[0] = self.dqdt[1]
        
        return self.update0(A, M, W, dt, num)

    def update10(self, A, M, W, dt, num=0):        
        self.dqdt = self.Q.d_dt(W)
        self.Q.set(Add(self.Q(), Times(self.dqdt,dt)))        
        return self.update1(A, M, W, dt, num)

    def update20(self, A, M, W, dt, num=0):        
        self.dqdt = self.Q.d_dt(W)
        self.Q.set(Add(self.Q(), Times(self.dqdt,dt)))        
        return self.update2(A, M, W, dt, num)
    
    def update_(self, A, M, W, dt, num=0):
        self.dqdt = self.Q.d_dt(W)
        beta = 0.25
        QestByW = Add(self.Q(), Times(self.dqdt,dt*beta))
        self.Q.set(QestByW)
        return self.Q.set(Normalize(self.Q()))

    def update__(self, A, M, W, dt, num=0):
        self.dqdt = self.Q.d_dt(W)
        beta = 0.25
        QestByW = Add(self.Q(), Times(self.dqdt,dt*beta))
        self.update20(A, M, W, dt, num)        
        return self.Q.set(Normalize(Add(self.Q(),QestByW)))

    def updateMadwick(self, accel, mag, gyro, dt):
        mx, my, mz = Normalize(mag)  # Units irrelevant (normalised)
        # Units irrelevant (normalised)
        ax, ay, az = Normalize(accel)
        az = -az
        my = - my
        mz = - mz
        gx, gy, gz = gyro  # Units deg/s
        q1, q2, q3, q4 = self.Q()   # short name local variable for readability
        # Auxiliary variables to avoid repeated arithmetic
        _2q1 = 2 * q1
        _2q2 = 2 * q2
        _2q3 = 2 * q3
        _2q4 = 2 * q4
        _2q1q3 = 2 * q1 * q3
        _2q3q4 = 2 * q3 * q4
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q1q4 = q1 * q4
        q2q2 = q2 * q2
        q2q3 = q2 * q3
        q2q4 = q2 * q4
        q3q3 = q3 * q3
        q3q4 = q3 * q4
        q4q4 = q4 * q4

        # Reference direction of Earth's magnetic field
        _2q1mx = 2 * q1 * mx
        _2q1my = 2 * q1 * my
        _2q1mz = 2 * q1 * mz
        _2q2mx = 2 * q2 * mx
        hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
        hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4
        _2bx = Sqrt(hx * hx + hy * hy)
        _2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4
        _4bx = 2 * _2bx
        _4bz = 2 * _2bz

        # Gradient descent algorithm corrective step
        s1 = (-_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4)
             + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
             + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        s2 = (_2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az)
             + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4)
             + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        s3 = (-_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az)
             + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
             + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
             + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        s4 = (_2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4)
              + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
              + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

         # Gradient decent algorithm corrective step
        # _4q1 = 4 * q1
        # _4q2 = 4 * q2
        # _4q3 = 4 * q3
        # _8q2 = 8 * q2
        # _8q3 = 8 * q3
        # q1q1 = q1 * q1
        # q2q2 = q2 * q2
        # q3q3 = q3 * q3
        # q4q4 = q4 * q4
         
        # s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
        # s2 = _4q2 * q4q4 - _2q4 * ax + 4 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
        # s3 = 4 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
        # s4 = 4 * q2q2 * q4 - _2q2 * ax + 4 * q3q3 * q4 - _2q3 * ay

        # s1,s2,s3,s4 = Normalize([s1,s2,s3,s4])

        # Compute rate of change of quaternion

        beta = radians(40)*sqrt(3.0 / 4.0)
        dqdt = Minus(self.Q.d_dt(gyro))
        qDot1 = dqdt[0] - beta * s1
        qDot2 = dqdt[1] - beta * s2
        qDot3 = dqdt[2] - beta * s3
        qDot4 = dqdt[3] - beta * s4

        # Integrate to yield quaternion
        q1 += qDot1 * dt
        q2 += qDot2 * dt
        q3 += qDot3 * dt
        q4 += qDot4 * dt
        
        self.Q.set(Normalize([q1,q2,q3,q4]))

    # -------------------------------------------------------- #
    def Rs(self, vIN):
        return self.Q.Rs(vIN)

    def Rv(self, vIN):
        return self.Q.Rv(vIN)

    def yaw(self):
        return self.Q.yaw()

    def pitch(self):
        return self.Q.pitch()

    def roll(self):
        return self.Q.roll()

    def YPR(self):
        return self.Q.YPR()

    def dQ(self, A, M):
        return Minus(Dot(Inverse(self.dFdq(A, M)), self.F(A, M)))

    def F(self, A, M):
        # AM is a list consisted of from Accel and Mag measured by the sensor
        mc = self.mc
        ms = self.ms
        a, b, c, d = self.Q()
        u0, u1, u2 = A
        u3, u4, u5 = M
        a2b2c2d2 = a**2+b**2+c**2+d**2
        return [2*a*a2b2c2d2 + c*u0 - b*u1 + a*u2 + (-(a*mc) - c*ms)*u3 + (-(d*mc) + b*ms)*u4 + (c*mc - a*ms)*u5,2*a2b2c2d2*b + d*u0 - a*u1 - b*u2 + (-(b*mc) - d*ms)*u3 + (-(c*mc) + a*ms)*u4 + (-(d*mc) + b*ms)*u5,2*a2b2c2d2*c + a*u0 + d*u1 - c*u2 + (c*mc - a*ms)*u3 + (-(b*mc) - d*ms)*u4 + (a*mc + c*ms)*u5,2*a2b2c2d2*d + b*u0 + c*u1 + d*u2 + (d*mc - b*ms)*u3 + (-(a*mc) - c*ms)*u4 + (-(b*mc) - d*ms)*u5]

    def dFdq(self, A, M):
        # AM is a list consisted of from Accel and Mag measured by the sensor
        mc = self.mc
        ms = self.ms
        a, b, c, d = self.Q()
        u0, u1, u2 = A
        u3, u4, u5 = M
        a2 = a**2
        b2 = b**2
        c2 = c**2
        d2 = d**2
        return [[2*(3*a2 + b2 + c2 + d2) + u2 - mc*u3 - ms*u5,4*a*b - u1 + ms*u4,4*a*c + u0 - ms*u3 + mc*u5,4*a*d - mc*u4],
                [4*a*b - u1 + ms*u4,2*(a2 + 3*b2 + c2 + d2) - u2 - mc*u3 + ms*u5,4*b*c - mc*u4,4*b*d + u0 - ms*u3 - mc*u5],
                [4*a*c + u0 - ms*u3 + mc*u5,4*b*c - mc*u4,2*(a2 + b2 + 3*c2 + d2) - u2 + mc*u3 + ms*u5,4*c*d + u1 - ms*u4],
                [4*a*d - mc*u4,4*b*d + u0 - ms*u3 - mc*u5,4*c*d + u1 - ms*u4,2*(a2 + b2 + c2 + 3*d2) + u2 + mc*u3 - ms*u5]]

        # return [[u2 - mc*u3 - ms*u5 + (3*a2 + b2 + c2 + d2)*(u02 + u12 + u22 + u32 + u42 + u52),u1 - ms*u4 + 2*a*b*(u02 + u12 + u22 + u32 + u42 + u52),-u0 + ms*u3 - mc*u5 + 2*a*c*(u02 + u12 + u22 + u32 + u42 + u52),mc*u4 + 2*a*d*(u02 + u12 + u22 + u32 + u42 + u52)],
        #         [u1 - ms*u4 + 2*a*b*(u02 + u12 + u22 + u32 + u42 + u52),-u2 - mc*u3 + ms*u5 + (a2 + 3*b2 + c2 + d2)*(u02 + u12 + u22 + u32 + u42 + u52),-(mc*u4) + 2*b*c*(u02 + u12 + u22 + u32 + u42 + u52),u0 - ms*u3 - mc*u5 + 2*b*d*(u02 + u12 + u22 + u32 + u42 + u52)],
        #         [-u0 + ms*u3 - mc*u5 + 2*a*c*(u02 + u12 + u22 + u32 + u42 + u52),-(mc*u4) + 2*b*c*(u02 + u12 + u22 + u32 + u42 + u52),-u2 + mc*u3 + ms*u5 + (a2 + b2 + 3*c2 + d2)*(u02 + u12 + u22 + u32 + u42 + u52),u1 - ms*u4 + 2*c*d*(u02 + u12 + u22 + u32 + u42 + u52)],
        #         [mc*u4 + 2*a*d*(u02 + u12 + u22 + u32 + u42 + u52),u0 - ms*u3 - mc*u5 + 2*b*d*(u02 + u12 + u22 + u32 + u42 + u52),u1 - ms*u4 + 2*c*d*(u02 + u12 + u22 + u32 + u42 + u52),u2 + mc*u3 - ms*u5 + (a2 + b2 + c2 + 3*d2)*(u02 + u12 + u22 + u32 + u42 + u52)]]

def main():
    import math
    import matplotlib.pyplot as plt
    theta = 50/180*math.pi
    A = [0, 0, -1]  # sensor
    M = [math.cos(theta), 0, math.sin(theta)]  # sensor
    #
    l = [0, 0, 1]
    solution = [math.cos(theta/2.), l[0]*math.sin(theta/2.),
                l[1]*math.sin(theta/2.), l[2]*math.sin(theta/2.)]
    #
    # initial values
    f = fusion(Normalize([0.8, .0, .0, -0.45399049973954675]))
    r = []
    t = []
    for i in range(30):
        t.append(i)
        # print('Norm(dq)=', Norm(dq),
        #       'r = ',Norm(Subtract(solution,f.Q())),
        #       'F = ',f.F(A,M)
        #       )
        # f.Q.set((Add(f.Q(), dq)))
        W = [0., 0., 0.]
        dt = 0.
        f.update(A, M, W, dt, 0)
        r.append(f.dq)
        print(f.F(A, M))
        # if Norm(dq) < 1E-5:
        #     break

    fig = plt.figure()  # 図を生成
    ax = plt.axes()
    ax.plot(t, r)
    print('solution = ', solution)
    print('Q = ', f.Q())
    print('r = ', Subtract(solution, f.Q()))
    print('norm =', Norm(Subtract(solution, f.Q())))
    plt.pause(10)


if __name__ == "__main__":
    main()
