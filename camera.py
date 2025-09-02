import cv2
import tkinter as tk
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self, window_title="Webcam Capture"):
        # Initialize camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Create Tkinter window
        self.root = tk.Tk()
        self.root.title(window_title)

        # Maximize (with borders)
        try:
            self.root.state("zoomed")          # Windows
        except:
            self.root.attributes("-zoomed", 1) # Linux/Mac

        # Video frame (fills all space above buttons)
        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.pack(fill="both", expand=True, side="top")

        # Use Canvas instead of Label so we control drawing
        self.canvas = tk.Canvas(self.video_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Button frame (fixed at bottom, no expansion)
        self.btn_frame = tk.Frame(self.root, height=60)
        self.btn_frame.pack(fill="x", side="bottom")

        self.btn = tk.Button(self.btn_frame, text="Take Picture", command=self.take_picture)
        self.btn.pack(side="left", padx=10, pady=10)

        self.exit_btn = tk.Button(self.btn_frame, text="Exit", command=self.safe_exit)
        self.exit_btn.pack(side="right", padx=10, pady=10)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)

        # Start updating frames
        self.update_frame()

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Get canvas size
                win_w = self.canvas.winfo_width()
                win_h = self.canvas.winfo_height()

                if win_w > 1 and win_h > 1:
                    h, w = frame.shape[:2]
                    aspect = w / h

                    # Scale to fit inside canvas
                    if win_w / win_h > aspect:
                        new_h = win_h
                        new_w = int(new_h * aspect)
                    else:
                        new_w = win_w
                        new_h = int(new_w / aspect)

                    frame_resized = cv2.resize(frame, (new_w, new_h))

                    # Convert to Tk image
                    cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv2image)
                    imgtk = ImageTk.PhotoImage(image=img)

                    # Save a copy of the "what you see" frame
                    self.current_display_frame = cv2image

                    # Clear canvas and center image
                    self.canvas.delete("all")
                    self.canvas.imgtk = imgtk  # keep reference
                    x = (win_w - new_w) // 2
                    y = (win_h - new_h) // 2
                    self.canvas.create_image(x, y, anchor="nw", image=imgtk)

        self.root.after(10, self.update_frame)

    def take_picture(self, filename="snapshot.png"):
        if hasattr(self, "current_display_frame"):
            # Save the resized frame you actually see
            img_bgr = cv2.cvtColor(self.current_display_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filename, img_bgr)
            print(f"📸 Picture saved as {filename}")
        else:
            print("⚠️ No frame available yet!")

    def safe_exit(self):
        print("Exiting program safely...")
        self.release()
        self.root.after(100, self.root.destroy)

    def run(self):
        self.root.mainloop()

    def release(self):
        if self.cap.isOpened():
            self.cap.release()


if __name__ == "__main__":
    app = WebcamApp()
    app.run()
