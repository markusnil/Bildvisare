import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
from drive_utils import get_service, list_files, upload_file, download_file
from datetime import datetime
import camera


shared_folder_id = "18l_kSviqElZrFXgI_y9WsKaFeBtFpyp-"

# Authenticate and get service
service = get_service()

# Get files that are available on drive:
files = list_files(service, folder_id=shared_folder_id)
for f in files:
    print(f"{f['name']} \t ({f['id']})")


local_images = []
# Download files
for f in files:
    download_file(service, f['id'], f['name'], dest_dir="./Images")
    local_images.append(f['name'])

# Variables for slideshow
Num_images = len(local_images)
imagecounter = 0
mycamera = None

#
#   Function for toggling fullscreen
#
def toggle_fs(dummy=None):
    state = False if root.attributes('-fullscreen') else True
    root.attributes('-fullscreen', state)
    if not state:
        root.geometry('700x500')

def setPhoto(filename):
    # Get the size of the label
    w = lbl.winfo_width()
    h = lbl.winfo_height()

    # If width or height is 0, try again after a short delay
    if w <= 1 or h <= 1:
        lbl.after(100, lambda: setPhoto(filename))
        return

    # Open image
    image = Image.open(filename)

    # Compute scale while keeping aspect ratio
    img_w, img_h = image.size
    scale = min(w / img_w, h / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)

    # Resize image
    image = image.resize((new_w, new_h), Image.LANCZOS)

    # Create white background
    background = Image.new("RGB", (w, h), (255, 255, 255))

    # Paste resized image centered
    x = (w - new_w) // 2
    y = (h - new_h) // 2
    background.paste(image, (x, y))

    # Convert to Tkinter format
    imgtk = ImageTk.PhotoImage(background)

    # Update label
    lbl.imgtk = imgtk
    lbl.configure(image=imgtk)

def slideshow():
    global imagecounter
    if not local_images:
        return  # nothing to show
    filename = os.path.join("./Images", local_images[imagecounter])
    setPhoto(filename)
    imagecounter = (imagecounter + 1) % Num_images
    root.after(5000, slideshow)

def startcamera():
    global mycamera
    # Stop slideshows
    mycamera = camera.WebcamApp()
    mycamera.run()


root = tk.Tk()
root.attributes('-fullscreen', True)
root.bind('<Escape>', toggle_fs)
root.bind('<Button-1>', toggle_fs)
#root.bind('c', lambda e: startcamera())    # Press 'c' for camera
root.title("Presentation")

# Label for video feed
lbl = tk.Label(root)
lbl.pack(fill=tk.BOTH, expand=True)


slideshow()

root.mainloop()
