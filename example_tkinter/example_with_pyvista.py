import os
import tkinter as tk
import pyvista as pv
from pyvistaqt import BackgroundPlotter

# Get a list of all .obj files in the current directory
files = [f for f in os.listdir(
    '.') if os.path.isfile(f) and f.endswith('.obj')]

root = tk.Tk()

plotter = BackgroundPlotter()
actors = {}

for file in files:
    # Load each .obj file and add it to the plotter
    mesh = pv.read(file)
    actor = plotter.add_mesh(mesh)

    # Initially hide each actor
    actor.SetVisibility(0)
    actors[file] = actor

    # Create a toggle button for each .obj file
    button = tk.Checkbutton(root, text=file, variable=tk.IntVar(),
                            command=lambda actor=actor: actor.SetVisibility(not actor.GetVisibility()))
    button.pack()

root.mainloop()
