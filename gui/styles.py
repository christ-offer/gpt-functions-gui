
from main import ChatbotGUI
from ttkthemes import ThemedTk
from tkinter import ttk

class Styles:
    def __init__(self):
        ChatbotGUI.default_font = ("Helvetica", 12)
        ChatbotGUI.default_bg_color = "#FFFFFF"
        ChatbotGUI.default_fg_color = "#000000"
        ChatbotGUI.root = ThemedTk(theme="black") # Choose a suitable theme
        ChatbotGUI.root.title('Personal Assistant')
        ChatbotGUI.root.grid_rowconfigure(0, weight=1)
        ChatbotGUI.root.grid_columnconfigure(0, weight=1)  # Give sidebar and main frame different weight
        ChatbotGUI.root.grid_columnconfigure(1, weight=4)
        ChatbotGUI.conversation = []  
        ChatbotGUI.style = ttk.Style()
        ChatbotGUI.style.configure('TButton', font=('Ubuntu', 14))
        ChatbotGUI.root.option_add('*foreground', 'black')  # Setting default text color to black

    def apply_default_style(self, widget):
        widget.config(font=self.default_font, bg=self.default_bg_color, fg=self.default_fg_color)
    
    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.root.set_theme(selected_theme)
