from tkinter import Tk,Label, Entry,Button, StringVar, Frame, BOTH
import os
from runner import run
"""
def check_valid_entry(entry):
    # currently an entry needs to be set in a form such that it is companyticker:exchange
    # exchange is not necessary if its a US company/ a private company
    try:
        info = entry.split(':')
        company =  info[0]
        exchange = info[1]
    except:
        company = entry

    reuters_tickers ={

        'Eu'





    }
"""




root = Tk()
root.title('Profile Generator')

root.geometry("500x500")

frame = Frame(master = root,bg = 'white')
frame.grid_propagate(0)
frame.pack(fill = BOTH, expand = 1)




ticker = StringVar()
company = StringVar()

print(str(ticker))
Label(master = frame,text = 'Please enter the Yahoo ticker of the company. If it is private, enter nothing.').pack()
Entry(master = frame, textvariable = ticker).pack()
Label(master = frame,text = 'Please enter the name of the company').pack()
Entry(master= frame, textvariable = company).pack()


def execute(ticker,company):
    try:
        run(ticker.get(),company.get())
        root.destroy()
    except:
        tk.messagebox.showerror('Error','This is an invalid company or ticker. Please try again.')
# in command I can call any function that I want. Now I need to create a function that effectively
# checks is the submission is a valid submission, and continues if so and doesn't continue if it isn't
Button(master = frame, text = 'Submit',command = lambda: execute(ticker,company)).pack()
Z = Label(master = frame, text = '')

#run(str(ticker),str(company)
# this is used to bring the app to the front in a MAC
# for windows, i would use root.lift() instead
os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')


root.mainloop()







"""
# window is the tkinter object -- ie the box that comes out
window = tk.Tk()



# title is the top part of the box that shows up
window.title("omg this is woorking")

coolFrame = tk.Frame(window)

# can put objects in frames rather than just the window, so that way you can seperate the box into different frames
# then you can have different things in different frames


# tkinter has 21 widgets
# in general, to insantiate a widget this is how it works:
# "tk.widget_name(root window (ie the tkinter object) , properties/configuration)" sometiems will need to add .method() at the end for positioning / other properties

tk.Label(coolFrame,text = 'This is our first label').pack()

tk.Button(coolFrame,text = 'This is a button').pack()


label2 = tk.Label(window, text = 'this is the second label')
label2.pack()

# window will have window.mainloop() which is the box that shows up (until I cancel it)

window.mainloop()

"""