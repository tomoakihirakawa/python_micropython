import tkinter as tk


def display_selection():
    label.config(text="selected: " + str(var.get()))


window = tk.Tk()
window.title('My Window')
window.geometry('200x100')

var = tk.IntVar()

radio1 = tk.Radiobutton(window, text='Option A',
                        variable=var, value=1, command=display_selection)
radio1.pack()

radio2 = tk.Radiobutton(window, text='Option B',
                        variable=var, value=2, command=display_selection)
radio2.pack()

label = tk.Label(window, text='')
label.pack()

window.mainloop()
