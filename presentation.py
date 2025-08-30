import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
from drive_utils import get_service, list_files, upload_file, download_file
from datetime import datetime

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
    download_file(service, f['id'], f['name'], dest_dir=".\Images")
    local_images.append(f['name'])

# Variables for slideshow
Num_images = len(local_images)
imagecounter = 0


#
#   Function for toggling fullscreen
#
def toggle_fs(dummy=None):
    state = False if root.attributes('-fullscreen') else True
    root.attributes('-fullscreen', state)
    if not state:
        root.geometry('700x500')

def setPhoto(filename):
    imgtk = ImageTk.PhotoImage(Image.open(filename))
    lbl.imgtk = imgtk
    lbl.configure(image=imgtk)

def slideshow():
    global imagecounter
    if not local_images:
        return  # nothing to show
    filename = os.path.join(".\Images", local_images[imagecounter])
    setPhoto(filename)
    imagecounter = (imagecounter + 1) % Num_images
    root.after(5000, slideshow)


root = tk.Tk()
root.attributes('-fullscreen', True)
root.bind('<Escape>', toggle_fs)
root.title("Presentation")

# Label for video feed
lbl = tk.Label(root)
lbl.pack(fill=tk.BOTH, expand=True)

#imgtk = ImageTk.PhotoImage(Image.open("snapshot_2025_8_30_16_59.png"))
#lbl.imgtk = imgtk
#lbl.configure(image=imgtk)

slideshow()

root.mainloop()