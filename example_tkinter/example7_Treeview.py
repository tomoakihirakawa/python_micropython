import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title('My Window')
window.geometry('200x100')

tree = ttk.Treeview(window)

tree["columns"] = ("Name", "Age")

tree.column("#0", width=0, stretch=tk.NO)
tree.column("Name", anchor=tk.W, width=120)
tree.column("Age", anchor=tk.W, width=80)

tree.heading("#0", text="", anchor=tk.W)
tree.heading("Name", text="Name", anchor=tk.W)
tree.heading("Age", text="Age", anchor=tk.W)

tree.insert("", 0, text="", values=("😃", 20))
tree.insert("", 2, text="", values=("B", 20))
tree.insert("", 5, text="", values=("C", 20))


def update_tree():
    tree.insert("", 6, text="", values=("D", 30))


button = tk.Button(window, text='Change', command=update_tree)
button.pack()

tree.pack()

window.mainloop()
