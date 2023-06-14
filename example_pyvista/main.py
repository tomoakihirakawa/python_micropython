import pyvista as pv
from pyvista import examples

mesh = examples.load_airplane()

plotter = pv.Plotter()
plotter.add_mesh(mesh, color='tan')
cpos = plotter.show()

mesh2 = examples.download_doorman()
mesh2.plot(cpos="xy")
plotter.add_mesh(mesh2, color='tan')
cpos = plotter.show()

