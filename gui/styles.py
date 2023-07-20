from ttkthemes import ThemedTk
from tkinter import ttk

class Styles:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.default_font = ("Helvetica", 12)
        self.default_bg_color = "#FFFFFF"
        self.default_fg_color = "#000000"
        self.root = ThemedTk(theme="black")  # Choose a suitable theme
        self.root.title('Personal Assistant')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)  # Give sidebar and main frame different weight
        self.root.grid_columnconfigure(1, weight=4)
        self.conversation = []  
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Ubuntu', 14))
        self.root.option_add('*foreground', 'black')  # Setting default text color to black

    def get_root(self):
        return self.root

    def apply_default_style(self, widget):
        widget.config(font=self.default_font, bg=self.default_bg_color, fg=self.default_fg_color)
    
    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.root.set_theme(selected_theme)