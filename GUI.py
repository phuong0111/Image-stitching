import tkinter as tk
from tkinter import filedialog
import shutil
import os
from tkinter import messagebox
import cv2  # Import OpenCV for image stitching
from stitched import *
from overlay import *


def get_desktop_path():
    """Returns the path to the user's desktop."""
    return os.path.join(os.path.expanduser("~"), "Desktop")


def check_image_type(image_path):
    """Checks the image format (replace with more robust logic if needed)."""
    # Basic check for common image formats
    # return image_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
    return True


def stitch_images(folder_path, output_path):
    """Stitches images within a folder using OpenCV (replace with your stitching logic)."""
    images = []
    for filename in os.listdir(folder_path):
        image_path = os.path.join(folder_path, filename)
        if check_image_type(image_path):
            images.append(cv2.imread(image_path))

    if not images:
        messagebox.showerror("Error", "No valid images found in the folder.")
        return

    # Replace with your preferred stitching algorithm (e.g., cv2.Stitcher_create())
    stitcher = cv2.Stitcher_create()
    status, stitched_image = stitcher.stitch(images)

    if not status:
        messagebox.showerror("Error", "Stitching failed.")
        return

    cv2.imwrite(output_path, stitched_image)
    messagebox.showinfo("Success", "Images stitched successfully!")


def browse_and_stitch_folder():
    """Opens a file dialog, selects a folder, and stitches the images."""
    folder_path = filedialog.askdirectory(initialdir="/Users/xuanphuong/Desktop/project/python/Image Stitching/V1/Data/Xray-image")
    if folder_path:
        try:
            dataset_name = os.path.basename(folder_path)
            stitched(dataset_name=dataset_name)
            messagebox.showinfo("Success", "Images stitched successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def browse_and_overlay_folder():
    """Opens a file dialog, selects a folder, and stitches the images."""
    folder_path = filedialog.askdirectory(
        initialdir="/Users/xuanphuong/Desktop/project/python/Image Stitching/V1/Data/Xray-image"
    )
    if folder_path:
        try:
            dataset_name = os.path.basename(folder_path)
            overlay(dataset_name=dataset_name, alpha=0.2, beta=0.8)
            messagebox.showinfo("Success", "Images overlay successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def browse_and_move_xray_folder():
    """Opens a file dialog, checks for X-ray image (replace with your logic), and moves the folder."""
    folder_path = filedialog.askdirectory(initialdir=get_desktop_path())
    if folder_path:
        xray_destination = "/Users/xuanphuong/Desktop/project/python/Image Stitching/V1/Data/Xray-image"  # Replace with your X-ray destination path

        if not check_image_type(folder_path):  # Replace with your X-ray image check
            messagebox.showerror("Error", "Folder does not contain an X-ray image.")
            return

        move_folder(folder_path, xray_destination)


def browse_and_move_optical_folder():
    """Opens a file dialog, checks for optical image (replace with your logic), and moves the folder."""
    folder_path = filedialog.askdirectory(initialdir=get_desktop_path())
    if folder_path:
        optical_destination = "/Users/xuanphuong/Desktop/project/python/Image Stitching/V1/Data/Optical-image"  # Replace with your optical destination path

        if not check_image_type(folder_path):  # Replace with your optical image check
            messagebox.showerror("Error", "Folder does not contain an optical image.")
            return

        move_folder(folder_path, optical_destination)


def move_folder(folder_path, destination_path):
    """Moves the folder to the specified destination."""

    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder does not exist.")
        return

    # Construct the destination folder path (assuming folder name is extracted from path)
    folder_name = os.path.basename(folder_path)
    destination_folder_path = os.path.join(destination_path, folder_name)

    if os.path.exists(destination_folder_path):
        messagebox.showerror(
            "Error", "Folder with the same name already exists in the destination."
        )
        return

    try:
        shutil.move(folder_path, destination_path)
        messagebox.showinfo("Success", "Folder moved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move folder: {e}")


# Create the main window
window = tk.Tk()
window.title("Move Folders")

# Labels
xray_label = tk.Label(window, text="X-ray Folder:")
xray_label.pack()

optical_label = tk.Label(window, text="Optical Folder:")
optical_label.pack()

# Buttons
xray_button = tk.Button(
    window, text="Browse and Move X-ray Folder", command=browse_and_move_xray_folder
)
xray_button.pack()

optical_button = tk.Button(
    window,
    text="Browse and Move Optical Folder",
    command=browse_and_move_optical_folder,
)
optical_button.pack()

stitch_button = tk.Button(
    window, text="Stitch Images", command=browse_and_stitch_folder
)
stitch_button.pack()

overlay_button = tk.Button(
    window, text="Overlay Images", command=browse_and_overlay_folder
)
overlay_button.pack()

window.mainloop()
