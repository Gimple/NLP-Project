import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import pytesseract
from autoCleaner import clean_text, load_wordlist

# =======================
# TESSERACT PATH
# =======================
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if sys.platform.startswith("win"):
    if os.path.exists(DEFAULT_TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH


class OCRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fake News Detector")
        self.geometry("900x600")
        self._create_widgets()

    def _create_widgets(self):
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Left: image area
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left, bg="#222", width=480, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=6)

        ttk.Button(btn_frame, text="Paste Image (Ctrl+V)", command=self.paste_image).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Open File...", command=self.open_file).pack(side=tk.LEFT, padx=6)
        # ttk.Button(btn_frame, text="From Clipboard (ImageGrab)", command=self.grab_clipboard).pack(side=tk.LEFT)

        # Right: extracted text area
        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Extracted Text:").pack(anchor=tk.W)
        self.text = tk.Text(right, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True)

        # Status bar area
        self.status = ttk.Label(self, text="Ready", anchor=tk.W)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        # Internal image 
        self._image = None

        # Bind paste
        self.bind_all('<Control-v>', lambda e: self.paste_image())

    def set_status(self, msg: str):
        self.status.config(text=msg)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff'), ('All files','*.*')])
        if not path:
            return
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror('Open image', f'Failed to open image: {e}')
            return
        self._set_image(img)
        self._run_ocr_async(img)

    def paste_image(self):  
        # PviaImageGrab
        try:
            img = ImageGrab.grabclipboard()
        except Exception:
            img = None
        if img is None:
            messagebox.showinfo('Paste', 'No image found in clipboard. Try using Windows+Shift+S to take a screenshot and then paste.')
            return

        if isinstance(img, list):
            # List of Filenames
            try:
                img = Image.open(img[0])
            except Exception as e:
                messagebox.showerror('Clipboard', f'Cannot open clipboard file: {e}')
                return
        self._set_image(img)
        self._run_ocr_async(img)

    # def grab_clipboard(self):
    #     # Another explicit grab using ImageGrab
    #     try:
    #         img = ImageGrab.grab()
    #     except Exception as e:
    #         messagebox.showerror('Clipboard Grab', f'Error grabbing clipboard: {e}')
    #         return
    #     self._set_image(img)
    #     self._run_ocr_async(img)

    def _set_image(self, pil_image: Image.Image):
        # Resize2Fit Canvas
        self._image = pil_image.convert('RGB')
        cw = self.canvas.winfo_width() or 480
        ch = self.canvas.winfo_height() or 480
        img = self._image.copy()
        img.thumbnail((cw, ch), Image.LANCZOS)
        self._tkimg = ImageTk.PhotoImage(img)
        self.canvas.delete('all')
        self.canvas.create_image(cw//2, ch//2, image=self._tkimg)

    def _run_ocr_async(self, pil_image: Image.Image):
        self.set_status('Running OCR...')
        self.text.delete('1.0', tk.END)
        thread = threading.Thread(target=self._do_ocr_and_clean, args=(pil_image.copy(),), daemon=True)
        thread.start()

    def _do_ocr_and_clean(self, pil_image: Image.Image):
        try:
            # Convert2RGB/Run Tesseract
            raw_text = pytesseract.image_to_string(pil_image)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror('OCR error', str(e)))
            self.after(0, lambda: self.set_status('OCR failed'))
            return

        # Insert OCR TxT
        def insert_raw():
            self.text.insert('1.0', '--- OCR Output ---\n')
            self.text.insert(tk.END, raw_text + '\n\n')
        self.after(0, insert_raw)

        # Prepare Dictionary
        base_dir = os.path.dirname(__file__)
        csv_dir = os.path.join(base_dir, 'csv')
        eng_csv = os.path.join(csv_dir, 'english_words.csv')
        tagalog_csv = os.path.join(csv_dir, 'tagalog_words.csv')
        jejemon_csv = os.path.join(csv_dir, 'jejemon.csv')
        dictionary = load_wordlist([eng_csv, tagalog_csv, jejemon_csv])

        # Logger
        def gui_logger(msg: str):
            self.after(0, lambda: self.text.insert(tk.END, msg + '\n'))

        try:
            cleaned = clean_text(raw_text, dictionary, log=True, logger=gui_logger)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Cleaning error', str(e)))
            self.after(0, lambda: self.set_status('Cleaning failed'))
            return

        # Final
        def insert_cleaned():
            self.text.insert(tk.END, '\n--- Cleaned Output ---\n')
            self.text.insert(tk.END, cleaned + '\n')
            self.set_status('Done')
        self.after(0, insert_cleaned)


def main():
    app = OCRApp()
    app.mainloop()


if __name__ == '__main__':
    main()