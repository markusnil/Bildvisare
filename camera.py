import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time


class WebcamApp:
    def __init__(self, window_title="Webcam Capture"):
        # Initialize camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


        # Create Tkinter window
        self.root = tk.Tk()
        self.root.title(window_title)

        # Label for video feed
        self.lbl = tk.Label(self.root)
        self.lbl.pack()

        # Capture button
        self.btn = tk.Button(self.root, text="Take Picture", command=self.take_picture)
        self.btn.pack()

        # Handle window close (X button)
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)

        self.picture_taken = False

        # Start updating frames
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lbl.imgtk = imgtk
            self.lbl.configure(image=imgtk)

        if not self.picture_taken:
            self.lbl.after(10, self.update_frame)

    def take_picture(self, filename="snapshot.png"):
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite(filename, frame)
            print(f"Picture saved as {filename}")
            self.picture_taken = True
            time.sleep(2)
            self.safe_exit()

    def safe_exit(self):
        print("Exiting program safely...")
        self.release()
        self.root.after(100, self.root.destroy)


    def run(self):
        self.root.mainloop()
        

    def release(self):
        if self.cap.isOpened():
            self.cap.release()


# Example usage when run directly:
if __name__ == "__main__":
    app = WebcamApp()
    try:
        app.run()
    finally:
        app.release()

