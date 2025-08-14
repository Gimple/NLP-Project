import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from TransJeje.core import JejemonNormalizer

class JejemonTranslatorUI:
    def __init__(self, root):
        self.root = root
        self.normalizer = JejemonNormalizer()
        self.setup_ui()
        
    def setup_ui(self):
        # Configure main window
        self.root.title("TransJeje: Jejemon Translator Pro")
        self.root.geometry("900x700")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Create custom style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', background='#0a0a0a', foreground='#00ff88',font=('Arial', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', background='#0a0a0a', foreground='#ff6b6b', font=('Arial', 12))
        
        style.configure('Custom.TButton', background='#ff6b6b', foreground='white', font=('Arial', 11, 'bold'), borderwidth=0, focuscolor='none')
        
        style.map('Custom.TButton', background=[('active', '#ff5252'), ('pressed', '#ff1744')])
        
        style.configure('Action.TButton', background='#00ff88', foreground='#0a0a0a', font=('Arial', 12, 'bold'), borderwidth=0, focuscolor='none')
        
        style.map('Action.TButton', background=[('active', '#00e676'), ('pressed', '#00c853')])
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#0a0a0a')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title with glow effect
        title_label = ttk.Label(header_frame, text="TransJeje: Jejemon Translator Pro", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Transform your jejemon text into readable Filipino/English", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # Input section
        input_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='raised', bd=2)
        input_frame.pack(fill='x', pady=(0, 15))
        
        # Input label
        input_label = tk.Label(input_frame, text="📝 ENTER JEJEMON TEXT:", bg='#1a1a1a', fg='#00ff88', font=('Arial', 12, 'bold'))
        input_label.pack(anchor='w', padx=15, pady=(15, 5))
        
        # Input text area with custom styling
        self.input_text = scrolledtext.ScrolledText(input_frame, height=4, font=('Consolas', 11), bg='#2a2a2a', fg='#ffffff',
        insertbackground='#00ff88', selectbackground='#ff6b6b', selectforeground='#ffffff', wrap=tk.WORD, relief='flat', bd=5)

        self.input_text.pack(fill='x', padx=15, pady=(0, 15))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#0a0a0a')
        buttons_frame.pack(fill='x', pady=(0, 15))
        
        # Action buttons
        translate_btn = ttk.Button(buttons_frame, text="🚀 TRANSLATE", command=self.translate_text, style='Action.TButton')

        translate_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = ttk.Button(buttons_frame, text="🗑️ CLEAR", command=self.clear_all, style='Custom.TButton')

        clear_btn.pack(side='left', padx=(0, 10))
        
        copy_btn = ttk.Button(buttons_frame, text="📋 COPY RESULT", command=self.copy_result, style='Custom.TButton')
        
        copy_btn.pack(side='left', padx=(0, 10))
        
        add_word_btn = ttk.Button(buttons_frame, text="➕ ADD WORD", command=self.open_add_word_dialog, style='Custom.TButton')
        
        add_word_btn.pack(side='right')
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(0, 15))
        
        # Output section
        output_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='raised', bd=2)
        output_frame.pack(fill='both', expand=True)
        
        # Output label
        output_label = tk.Label(output_frame, text="✨ TRANSLATION RESULT:",  bg='#1a1a1a', fg='#00ff88', font=('Arial', 12, 'bold'))
        
        output_label.pack(anchor='w', padx=15, pady=(15, 5))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=6, font=('Consolas', 11), 
        bg='#2a2a2a', fg='#00ff88', insertbackground='#00ff88', selectbackground='#ff6b6b', selectforeground='#ffffff', wrap=tk.WORD, relief='flat', bd=5, state='disabled')
        
        self.output_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#0a0a0a')
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready to translate jejemon text...", bg='#0a0a0a', fg='#888888', font=('Arial', 10))
        
        self.status_label.pack(side='left')
        
        # Dictionary count
        dict_count = len(self.normalizer.jejemon_dict)
        dict_label = tk.Label(status_frame, text=f"Dictionary: {dict_count} words", bg='#0a0a0a', fg='#888888', font=('Arial', 10))
        
        dict_label.pack(side='right')
        
        # Bind Enter key to translate
        self.input_text.bind('<Control-Return>', lambda e: self.translate_text())
        
    def translate_text(self):
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("Warning", "Please enter some jejemon text to translate!")
            return
        
        # Start progress animation
        self.progress.start(10)
        self.status_label.config(text="Translating jejemon text...")
        
        # Disable translate button during processing
        self.root.after(100, lambda: self._process_translation(input_text))
        
    def _process_translation(self, text):
        try:
            time.sleep(0.5)

            result = self.normalizer.normalize_text(text)

            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)

            output = f"🎯 FINAL RESULT:\n{result['final_normalized']}\n\n"
            output += f"📋 PROCESSING PIPELINE (step by step):\n"
            for key in result:
                if key.startswith('step_'):
                    label = key.replace('step_', '').replace('_', ' ').capitalize()
                    output += f"{label}: {result[key]}\n"

            self.output_text.insert(1.0, output)
            self.output_text.config(state='disabled')

            self.progress.stop()
            self.status_label.config(text="Translation completed successfully!")

        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="Translation failed!")
            messagebox.showerror("Error", f"Translation failed: {str(e)}")
    
    def clear_all(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        self.status_label.config(text="Text cleared. Ready for new translation...")
    
    def copy_result(self):
        try:
            output_content = self.output_text.get(1.0, tk.END)
            if "🎯 FINAL RESULT:" in output_content:
                lines = output_content.split('\n')
                final_result = lines[1] if len(lines) > 1 else ""
                
                if final_result.strip():
                    self.root.clipboard_clear()
                    self.root.clipboard_append(final_result.strip())
                    self.status_label.config(text="Result copied to clipboard!")
                else:
                    messagebox.showinfo("Info", "No result to copy!")
            else:
                messagebox.showinfo("Info", "No translation result to copy!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {str(e)}")
    
    def open_add_word_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Jejemon Word")
        dialog.geometry("400x250")
        dialog.configure(bg='#1a1a1a')
        dialog.resizable(False, False)
        
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="➕ Add New Jejemon Word", 
                bg='#1a1a1a', fg='#00ff88', 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        tk.Label(dialog, text="Jejemon Word:", 
                bg='#1a1a1a', fg='#ffffff', 
                font=('Arial', 10)).pack(anchor='w', padx=30)
        
        jejemon_entry = tk.Entry(dialog, font=('Arial', 11), 
                               bg='#2a2a2a', fg='#ffffff',
                               insertbackground='#00ff88',
                               relief='flat', bd=5)
        jejemon_entry.pack(fill='x', padx=30, pady=(5, 15))
        
        tk.Label(dialog, text="Normal Word:", 
                bg='#1a1a1a', fg='#ffffff', 
                font=('Arial', 10)).pack(anchor='w', padx=30)
        
        normal_entry = tk.Entry(dialog, font=('Arial', 11), 
                              bg='#2a2a2a', fg='#ffffff',
                              insertbackground='#00ff88',
                              relief='flat', bd=5)
        normal_entry.pack(fill='x', padx=30, pady=(5, 20))
        
        btn_frame = tk.Frame(dialog, bg='#1a1a1a')
        btn_frame.pack(fill='x', padx=30)
        
        def add_word():
            jejemon_word = jejemon_entry.get().strip()
            normal_word = normal_entry.get().strip()
            
            if not jejemon_word or not normal_word:
                messagebox.showwarning("Warning", "Please fill in both fields!")
                return
            
            if self.normalizer.add_word_mapping(jejemon_word, normal_word):
                messagebox.showinfo("Success", f"Added mapping: '{jejemon_word}' → '{normal_word}'")
                dialog.destroy()

                dict_count = len(self.normalizer.jejemon_dict)
                self.status_label.config(text=f"Word added! Dictionary now has {dict_count} words.")
            else:
                messagebox.showerror("Error", "Failed to add word mapping!")
        
        add_btn = tk.Button(btn_frame, text="✅ Add Word", command=add_word, bg='#00ff88', fg='#0a0a0a', font=('Arial', 10, 'bold'), relief='flat', bd=0)
        
        add_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy, bg='#ff6b6b', fg='#ffffff', font=('Arial', 10, 'bold'), relief='flat', bd=0)
        
        cancel_btn.pack(side='left')
        
        jejemon_entry.focus()
        
        jejemon_entry.bind('<Return>', lambda e: normal_entry.focus())
        normal_entry.bind('<Return>', lambda e: add_word())

def main():
    root = tk.Tk()
    app = JejemonTranslatorUI(root)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()