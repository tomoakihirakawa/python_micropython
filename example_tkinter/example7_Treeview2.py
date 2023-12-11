import tkinter as tk
from tkinter import ttk


def toggle_emoji():
    selected = tree.selection()
    if selected:
        # Get the current values of the selected row
        values = tree.item(selected[0], 'values')
        # If the emoji is emoji1, change it to emoji2 and vice versa
        if values[2] == emoji1:
            tree.set(selected[0], 'Emoji', emoji2)
        else:
            tree.set(selected[0], 'Emoji', emoji1)


window = tk.Tk()
window.title("Treeview Emoji Toggle Example")
window.geometry("500x500")

# Define two emojis
emoji1 = "\U0001F600"  # Grinning face
emoji2 = "\U0001F642"  # Slightly smiling face

tree = ttk.Treeview(window)

# Define columns
tree['columns'] = ('ID', 'Name', 'Emoji')

# Format columns
tree.column('#0', width=0, stretch='no')  # first column is for tree nodes
tree.column('ID', anchor='center', width=80)
tree.column('Name', anchor='w', width=120)
tree.column('Emoji', anchor='center', width=80)

# Create headings
tree.heading('#0', text='', anchor='w')
tree.heading('ID', text='ID', anchor='center')
tree.heading('Name', text='Name', anchor='w')
tree.heading('Emoji', text='Emoji', anchor='center')

# Insert some items with emojis
tree.insert(parent='', index='end', iid=0, text='',
            values=('1', 'John Doe', emoji1))
tree.insert(parent='', index='end', iid=1, text='',
            values=('2', 'Jane Smith', emoji1))

tree.pack()

button = tk.Button(window, text="Toggle Emoji", command=toggle_emoji)
button.pack()

window.mainloop()
