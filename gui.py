import tkinter as tk
from tkinter import messagebox


master = tk.Tk()


master.title("Threshold Input")
# window = tk.Tk()
# window.geometry("100x100")


# def helloCallBack():
#    messagebox.showinfo( "Hello Python", "Hello World")


# button = tk.Button(window, text ="Hello", fg="Blue", command = helloCallBack)

# button.pack()
# window.mainloop()


def show_entry_fields():
    print("First Name: %s\nLast Name: %s" % (e1.get(), e2.get()))

tk.Label(master, 
         text="First Name").grid(row=0)
tk.Label(master, 
         text="Last Name").grid(row=1)

e1 = tk.Entry(master)
e2 = tk.Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

tk.Button(master, 
          text='Quit', fg="red",
          command=master.quit).grid(row=3, 
                                    column=0, 
                                    sticky=tk.W, 
                                    pady=4)
tk.Button(master, 
          text='Show', command=show_entry_fields).grid(row=3, 
                                                       column=1, 
                                                       sticky=tk.W, 
                                                       pady=4)

tk.mainloop()