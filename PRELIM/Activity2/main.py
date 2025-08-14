import tkinter as tk
from TransJeje.ui import JejemonTranslatorUI
import sys
import os

def main():
    try:
        root = tk.Tk()
        
        app = JejemonTranslatorUI(root)
        
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        root.mainloop() 
        
    except ImportError as e:
        print(f"Error importing {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()