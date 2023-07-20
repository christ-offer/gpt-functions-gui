import logging
from tkinter import ttk
from dotenv import load_dotenv


from gui.settings_tab import SettingsTab
from gui.chat_tab import ChatTab
from gui.file_tab import FileTab
from gui.styles import Styles

from constants import *

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
load_dotenv()

class ChatbotGUI:
    def __init__(self):
        self.styles = Styles(self)
        self.root = self.styles.get_root()
        
        self.total_tokens = 0
        self.total_cost = 0
        
        self.conversation = []

        # Create the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)

        # Create notebook (tab control)
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=0, rowspan=2, columnspan=2, sticky='nsew')

        # Create Chat Window Tab
        self.chat_window = ttk.Frame(self.tabControl)
        self.tabControl.add(self.chat_window, text='Chat')
        
        # Initialize ChatTab
        self.chat_tab = ChatTab(chat_window=self.chat_window, parent=self)
        self.chat_tab.create_widgets_chat()
        
        
        # Create File Manager Tab
        self.file_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.file_tab, text='Files')
        
        # Initialize FileTab
        self.file_tab = FileTab(file_tab=self.file_tab, parent=self)
        self.file_tab.create_widgets_file_manager()
        
        
        # Create Settings Tab
        self.settings = ttk.Frame(self.tabControl)
        self.tabControl.add(self.settings, text='Settings')
        
        # Initialize SettingsTab
        self.settings_tab = SettingsTab(settings=self.settings)
        self.settings_tab.settings = self.settings
        self.settings_tab.create_widgets_settings()

        self.is_loading = False
    

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    chatbot_gui = ChatbotGUI()
    chatbot_gui.run()