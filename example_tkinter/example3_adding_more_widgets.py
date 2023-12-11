import tkinter as tk


def change_text():
    label.config(text='Changed')


window = tk.Tk()
window.title('My Window')
window.geometry('200x100')

label = tk.Label(window, text='Hello, Tkinter!', bg='yellow', fg='black')
label.pack()

button = tk.Button(window, text='Change', command=change_text)
button.pack()

window.mainloop()
