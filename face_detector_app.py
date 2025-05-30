import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import cv2
import os

# --- Configuration ---
CASCADE_PATH = "haarcascade_frontalface_default.xml"

if not os.path.exists(CASCADE_PATH):
    try:
        root_check = tk.Tk()
        root_check.withdraw()
        messagebox.showerror("Error", f"Critical Error: Cascade file not found at '{os.path.abspath(CASCADE_PATH)}'.\n\nPlease download 'haarcascade_frontalface_default.xml' from OpenCV's GitHub and place it in the same directory as the script.\n\nThe application will now close.")
        root_check.destroy()
    except tk.TclError:
        print(f"CRITICAL ERROR: Cascade file not found at '{os.path.abspath(CASCADE_PATH)}'")
        print("Please download 'haarcascade_frontalface_default.xml' from OpenCV's GitHub and place it in the same directory as the script.")
        print("The application will now close.")
    exit()

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# --- Global Variables ---
original_image_tk = None # To keep a reference for Tkinter image objects

# --- Functions ---
def log_message(message):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)
    log_area.config(state=tk.DISABLED)

def update_image_display(pil_image, original_filename="image"):
    """Displays the given PIL image in the GUI."""
    global original_image_tk
    try:
        if pil_image is None:
            image_label.config(image='', text="No image to display")
            log_message("No image data to display.")
            return

        # Resize image to fit in the label (e.g., max 300x300)
        display_pil_image = pil_image.copy() # Work on a copy for thumbnail
        display_pil_image.thumbnail((300, 300))
        original_image_tk = ImageTk.PhotoImage(display_pil_image)

        image_label.config(image=original_image_tk)
        image_label.image = original_image_tk # Keep a reference!
        log_message(f"Image '{original_filename}' processed and displayed.")

    except Exception as e:
        log_message(f"Error updating image display: {e}")
        image_label.config(image='', text="Error displaying image")


def upload_and_process_image():
    result_label.config(text="Result: Awaiting image...", style="Neutral.Result.TLabel")
    image_label.config(image='', text="Uploaded image will appear here") # Clear previous image
    log_message("------------------------------------")
    log_message("Upload button clicked. Opening file dialog...")

    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*"))
    )

    if not file_path:
        log_message("No file selected.")
        return

    log_message(f"Selected file: {file_path}")
    detect_faces(file_path)

def detect_faces(image_path):
    log_message("Processing image for face detection...")
    pil_image_to_display = None # Initialize
    original_filename = os.path.basename(image_path)

    try:
        # Read the image using OpenCV
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            log_message("Error: Could not read image with OpenCV. File might be corrupted or not an image.")
            result_label.config(text="Result: Error reading image", style="Error.Result.TLabel")
            # Try to load with PIL for display if OpenCV fails
            try:
                pil_image_to_display = Image.open(image_path)
            except Exception as e_pil:
                log_message(f"Could not load image with PIL either: {e_pil}")
            update_image_display(pil_image_to_display, original_filename)
            return

        # Convert to grayscale (Haar cascades work better on grayscale)
        gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        log_message("Image converted to grayscale.")

        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        log_message(f"Face detection performed. Found {len(faces)} potential face(s).")

        if len(faces) > 0:
            result_label.config(text="Result: Yes, human face(s) detected!", style="Success.Result.TLabel")
            log_message("Human face(s) DETECTED.")
            # Draw rectangles on the original OpenCV image (img_cv)
            for (x, y, w, h) in faces:
                cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2) # Green rectangle
            log_message("Rectangles drawn on image.")
        else:
            result_label.config(text="Result: No human face detected.", style="Error.Result.TLabel")
            log_message("NO human face detected.")

        # Convert the (possibly modified) OpenCV image (BGR) to RGB for Pillow
        img_cv_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pil_image_to_display = Image.fromarray(img_cv_rgb) # Create Pillow image from array

    except Exception as e:
        log_message(f"Error during face detection or image processing: {e}")
        result_label.config(text="Result: Error during processing", style="Error.Result.TLabel")
        # If an error occurs during detection but we have the path, try to load with PIL
        if pil_image_to_display is None and os.path.exists(image_path):
            try:
                pil_image_to_display = Image.open(image_path)
                log_message("Displayed original image due to processing error.")
            except Exception as e_pil_fallback:
                log_message(f"Fallback PIL load failed: {e_pil_fallback}")
    
    finally: # Ensure image display is attempted
        update_image_display(pil_image_to_display, original_filename)


# --- GUI Setup ---
root = tk.Tk()
root.title("Human Face Identifier - Made By Ram Bapat www.linkedin.com/in/ram-bapat-barrsum-diamos")
root.geometry("550x700")

style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("TLabel", font=("Helvetica", 12))
style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
style.configure("LogHeader.TLabel", font=("Helvetica", 10, "italic"))

default_result_font = ("Helvetica", 14, "bold")
style.configure("Neutral.Result.TLabel", font=default_result_font, foreground="black")
style.configure("Success.Result.TLabel", font=default_result_font, foreground="green")
style.configure("Error.Result.TLabel", font=default_result_font, foreground="red")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(main_frame, text="Human Face Identifier", style="Header.TLabel")
title_label.pack(pady=(0, 15))
title_label = ttk.Label(main_frame, text="- Made By Ram Bapat -", style="Header.TLabel")
title_label.pack(pady=(0, 20))
title_label = ttk.Label(main_frame, text="www.linkedin.com/in/ram-bapat-barrsum-diamos", style="Header.TLabel")
title_label.pack(pady=(0, 25))

upload_button = ttk.Button(main_frame, text="Upload Image & Detect Faces", command=upload_and_process_image)
upload_button.pack(pady=10)

image_frame = ttk.Frame(main_frame, borderwidth=1, relief="sunken", width=310, height=310)
image_frame.pack(pady=10)
image_frame.pack_propagate(False)

image_label = ttk.Label(image_frame, text="Uploaded image will appear here", anchor="center")
image_label.pack(fill=tk.BOTH, expand=True)

log_header_label = ttk.Label(main_frame, text="Processing Logs:", style="LogHeader.TLabel")
log_header_label.pack(pady=(10,2), anchor='w')
log_area = scrolledtext.ScrolledText(main_frame, height=10, width=60, state=tk.DISABLED, wrap=tk.WORD, font=("Courier New", 10))
log_area.pack(pady=5, padx=0, fill=tk.BOTH, expand=True)

result_label = ttk.Label(main_frame, text="Result: Awaiting image...", style="Neutral.Result.TLabel", anchor="center")
result_label.pack(pady=20)

log_message("Application started. Please upload an image.")
log_message(f"Using cascade file: {os.path.abspath(CASCADE_PATH)}")

root.mainloop()

# Made by Ram Bapat (www.linkedin.com/in/ram-bapat-barrsum-diamos)