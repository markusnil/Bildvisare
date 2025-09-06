import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
from drive_utils import get_service, list_files, upload_file, download_file
from datetime import datetime
import camera
from pillow_heif import register_heif_opener

register_heif_opener()


shared_folder_id = "18l_kSviqElZrFXgI_y9WsKaFeBtFpyp-"

# Authenticate and get service
service = get_service()



# Variables for slideshow
imagecounter = 0
mycamera = None
local_images = []



def checkFilesAndDownload():
    global local_images
    global imagecounter
    # Get files that are available on drive:
    files = list_files(service, folder_id=shared_folder_id)
    local_images = []

    # Download files which are not already in /Images:
    for f in files:
        print(f"{f['name']} \t ({f['id']})")
        mime_type = f['mimeType']
        if not mime_type.startswith("application/vnd.google-apps"):
            download_file(service, f['id'], f['name'], dest_dir="./Images")
            local_images.append(f['name'])

    # Remove files that are in /Images but not on drive:
    directory = os.fsencode("./Images")
    for file in os.listdir(directory):
        print(file.decode('UTF-8'))
        status = False
        for f in files:
            if file.decode('UTF-8') == f['name']:
                status = True
        if not status:    
            fpath = os.path.join("./Images", file.decode('UTF-8'))
            if os.path.isfile(fpath):
                print("File not found, deleting: " + fpath)
                os.remove(fpath)

                

# Download files
checkFilesAndDownload()




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
    global local_images

    imagecounter = imagecounter + 1
    imagecounter = imagecounter % len(local_images)    

    if not local_images:
        return  # nothing to show
    filename = os.path.join("./Images", local_images[imagecounter])
    setPhoto(filename)
    if (imagecounter == (len(local_images)-1)):
        checkFilesAndDownload()
    root.after(10000, slideshow)

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
