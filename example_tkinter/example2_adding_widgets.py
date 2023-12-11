import tkinter as tk

window = tk.Tk()
window.title('My Window')
window.geometry('200x100')
window.configure(background='blue')

label = tk.Label(window, text="Hello, Tkinter!", bg='purple',
                 font=('Arial', 12), width=30, height=2)
label.pack()

window.mainloop()
