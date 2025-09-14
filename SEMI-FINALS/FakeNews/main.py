import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import main as run_ui


def main():
    try:
        app = QApplication(sys.argv)
        
        app.setApplicationName("Fake News Detector")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("NLP Project")
        
        app.setStyle('Fusion')
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        print("Starting Fake News Detector...")
        print("Application initialized successfully!")
        
        # Run the main UI
        run_ui()
        
    except ImportError as e:
        print(f"Error: Missing required dependencies. {e}")
        print("Please install required packages using: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
