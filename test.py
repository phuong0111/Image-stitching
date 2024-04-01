import os
import cv2
import matplotlib.pyplot as plt

# Define the number of rows and columns for the grid
rows = 1
cols = 2

# Assuming you have your image data loaded into a list called 'images'
# (replace 'images' with your actual data loading logic)
# Each element in 'images' should be a loaded image using libraries like OpenCV or Pillow

# Create a figure and adjust the layout
fig, axes = plt.subplots(rows, cols, figsize=(12, 6))  # Adjust figsize for image size
images = [
    cv2.imread(
        f"/Users/xuanphuong/Desktop/project/python/Image Stitching/V1/Data/Optical-image/Test-2/PCB/optical_PCB.jpg"
    ),
    cv2.imread(
        f"/Users/xuanphuong/Desktop/project/python/Image Stitching/V1/Output/SIFT/Test-2/PCB/image_stitched_4.jpg"
    ),
]

# Loop through images and display them on subplots
for i in range(rows):
    for j in range(cols):
        if i * cols + j < len(images):  # Check if we have enough images
            axes[j].imshow(images[i * cols + j])
            axes[j].set_xticks([])
            axes[j].set_yticks([])  # Hide unnecessary ticks
        else:
            axes[j].axis("off")  # Hide empty subplots

# Tight layout to avoid overlapping labels
plt.tight_layout()

# Display the images
plt.show()
