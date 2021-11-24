import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from time import sleep


class Plot3D():

    def __init__(self):
        import matplotlib.pyplot as plt
        self.fig = plt.figure()  # 図を生成
        self.ax3d = self.fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
        self.r = [-3., 3.]  # range
        self.ax3d.set_xlim(self.r)
        self.ax3d.set_ylim(self.r)
        self.ax3d.set_zlim(self.r)
        self.T = [0]
        self.X = []
        self.Y = []
        self.Z = []
        self.sc = self.ax3d.scatter([0.], [0.], [0.])
        self.sc._offsets3d = (self.X, self.Y, self.Z)
        print("Plot3D started")
        plt.pause(0.01)
        self.fig.canvas.draw()

    def __del__(self):
        try:
            plt.close(self.fig)
        except:
            pass

    def append(self, X_IN, Y_IN, Z_IN):
        self.X.append(X_IN)  # 図用にmagにデータを蓄積
        self.Y.append(Y_IN)  # 図用にmagにデータを蓄積
        self.Z.append(Z_IN)  # 図用にmagにデータを蓄積
        self.sc._offsets3d = (self.X, self.Y, self.Z)
        print("Plot3D append")
        plt.pause(0.01)
        self.fig.canvas.draw()
        plt.show(block=False)
        # plt.pause(.01)


def main():
    p = Plot3D()
    for i in range(100):
        p.append(1, i, 3)
        p.append(i, 2, 3)
        p.append(1, 0, i)
        p.append(1, 1, 1)
        plt.pause(.01)

    sleep(2)


if __name__ == "__main__":
    main()
