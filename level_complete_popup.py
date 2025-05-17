import tkinter as tk
from tkinter import ttk
import logging

class LevelCompletePopup:
    def __init__(self, parent):
        self.parent = parent
        self.popup_window = None

    def show(self, title="Level Complete", subtitle="Congratulations!", callback_next=None, callback_level_select=None, width=450, height=250):
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.lift()
            return self.popup_window

        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title(title)
        self.popup_window.transient(self.parent) # Keep popup on top of parent
        self.popup_window.grab_set() # Modal behavior

        # Calculate position to center on parent
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.popup_window.geometry(f"{width}x{height}+{x}+{y}")
        self.popup_window.resizable(False, False)

        # Style
        self.popup_window.configure(bg="#2E2E2E")
        s = ttk.Style()
        # Base style for Popup.TButton
        s.configure('Popup.TButton', font=('Helvetica', 12, 'bold'), padding=10, borderwidth=0, foreground='#FFFFFF', background='#0078D7', relief='raised')
        s.map('Popup.TButton',
            foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')],
            background=[('active', '#0078D7'), ('pressed', '#005A9E')],
            relief=[('pressed', 'sunken'), ('active', 'raised')])

        # Style for Next.Popup.TButton (Green)
        s.configure('Next.Popup.TButton', background='#28A745', foreground='#FFFFFF')
        s.map('Next.Popup.TButton',
            background=[('active', '#218838'), ('pressed', '#1E7E34')],
            foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')])

        # Style for Select.Popup.TButton (Blue)
        s.configure('Select.Popup.TButton', background='#007BFF', foreground='#FFFFFF')
        s.map('Select.Popup.TButton',
            background=[('active', '#0069D9'), ('pressed', '#005CBF')],
            foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')])

        main_frame = ttk.Frame(self.popup_window, padding="20 20 20 20", style='TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH)
        self.popup_window.configure(bg="#1e1e1e") # Dark background for the window itself
        # Ensure TFrame style is configured for the main_frame's background
        style_main_frame = ttk.Style()
        style_main_frame.configure('TFrame', background='#1e1e1e')


        title_label = ttk.Label(main_frame, text=title, font=("Helvetica", 20, "bold"), background='#1e1e1e', foreground='#E0E0E0')
        title_label.pack(pady=(0, 10))

        if subtitle:
            subtitle_label = ttk.Label(main_frame, text=subtitle, font=("Helvetica", 12), background='#1e1e1e', foreground='#C0C0C0', wraplength=width-60, justify=tk.CENTER)
            subtitle_label.pack(pady=(0, 25))
            
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(10,0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)


        def on_next():
            logging.info("'Next Level' chosen from level complete popup.")
            if callback_next:
                callback_next()
            self.close()

        def on_level_select():
            logging.info("'Level Select' chosen from level complete popup.")
            if callback_level_select:
                callback_level_select()
            self.close()

        next_button = ttk.Button(button_frame, text="Next Level", command=on_next, style='Next.Popup.TButton', width=18)
        next_button.grid(row=0, column=0, padx=10, sticky='ew')

        level_select_button = ttk.Button(button_frame, text="Level Select", command=on_level_select, style='Select.Popup.TButton', width=18)
        level_select_button.grid(row=0, column=1, padx=10, sticky='ew')
        
        button_frame.pack(pady=10, fill=tk.X)

        self.popup_window.focus_set()
        self.popup_window.lift()
        self.popup_window.attributes("-topmost", True)
        self.popup_window.after(100, lambda: self.popup_window.attributes("-topmost", False))

        return self.popup_window

    def close(self):
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
            self.popup_window = None
            if self.parent and self.parent.winfo_exists():
                 self.parent.grab_release() # Correctly release grab
                 self.parent.focus_set() # Return focus to parent
