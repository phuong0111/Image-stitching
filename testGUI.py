import os
import platform
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as box
import stitched
import overlay
from utility import *
import sys
from distutils.dir_util import copy_tree

import tkinter as tk

if os.name == "posix":
    desktop_path = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
else:
    desktop_path = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")


def add_xray_dataset():
    directory = filedialog.askdirectory(initialdir=desktop_path)
    if directory:
        target_directory = f"{os.curdir}/Data/Xray-image/{directory.split('/')[-1]}"
        mkdir_if_not_exist(target_directory)
        copy_tree(directory, target_directory)
        listbox.pack_forget()  # Hide the listbox
        processing_button.pack(side=LEFT)  # Show the processing button


def add_optical_dataset():
    directory = filedialog.askdirectory(initialdir=desktop_path)
    if directory:
        target_directory = f"{os.curdir}/Data/Optical-image/{directory.split('/')[-1]}"
        mkdir_if_not_exist(target_directory)
        copy_tree(directory, target_directory)
        listbox.pack_forget()  # Hide the listbox
        processing_button.pack(side=LEFT)  # Show the processing button


def stitch_images():
    processing_button.pack_forget()  # Hide the processing button
    listbox.pack(side=LEFT)  # Show the listbox


def overlay_images():
    print("Overlay images")


def dialog():
    box.showinfo("Selection", "Your Choice: " + listbox.get(listbox.curselection()))


root = Tk(className="Image Processing Toolkit")

# Create a menu
menu = Menu(root)
root.config(menu=menu)

# Create a frame to hold the textbox, entry, and submit button
frame = Frame(root)
frame.pack(expand=True, fill=BOTH)

# Create a label and add it to the frame
label = Label(frame, text="Choose dataset to process")
label.pack(side=LEFT)

listbox = Listbox(frame)
listbox.insert(1, "<filename>")
listbox.insert(2, "<filename>")
listbox.insert(3, "<filename>")

listbox.pack_forget()  # Hide the listbox initially

processing_button = Button(frame, text="Processing", command=stitch_images)
processing_button.pack(side=LEFT)  # Show the processing button initially

btn = Button(frame, text="View Info", command=dialog)

btn.pack(side=RIGHT, padx=5)
listbox.pack(side=LEFT)
frame.pack(padx=30, pady=30)

# Create menu options
add_dataset_action = Menu(menu, tearoff=0)
dataset_menu = Menu(add_dataset_action, tearoff=0)
image_processing_action = Menu(menu, tearoff=0)
processing_menu = Menu(image_processing_action, tearoff=0)

# Add sub-options to add dataset option
add_dataset_action.add_cascade(label="Xray", menu=dataset_menu)
add_dataset_action.add_command(label="Optical", command=add_optical_dataset)

# Add sub-options to image processing option
image_processing_action.add_command(label="Stitch images", command=stitch_images)
image_processing_action.add_command(label="Overlay images", command=overlay_images)

# Add menu options to menu
menu.add_cascade(label="Add dataset", menu=add_dataset_action)
menu.add_cascade(label="Processing", menu=image_processing_action)

root.mainloop()
