import os
import logging
import requests
import shutil
import markdown
import tkinter as tk
from tkinter import ttk, Listbox, Scrollbar, N, S, E, W, CENTER, scrolledtext, filedialog, Canvas, StringVar, OptionMenu, LabelFrame, Label, Entry, Button, Frame, messagebox, Menu
from ttkthemes import ThemedTk
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk
from dotenv import load_dotenv

from chatbot import run_conversation
from agents.image_agent import ImageAgent
from agents.csv_agent import CSVHandler
from agents.file_write_agent import FileWriter
from agents.help_agent import HelpAgent
from agents.history_agent import HistoryHandler
from agents.kb_agent import KnowledgebaseHandler
from agents.scrape_agent import Scraper
from agents.python_agent import PythonRepl
from agents.wikidata_agent import WikidataAgent
from constants import *

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

DIRECTORIES = [KB_DIR, HISTORY_DIR, CSV_DIR, IMG_DIR, CODE_DIR, LOG_DIR, DATA_DIR, PROJECTS_DIR]

load_dotenv()
image_agent = ImageAgent()
csv_agent = CSVHandler()

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

class FileManager:
    def __init__(self):
        # Check if directories exist and create them if they don't
        for directory in DIRECTORIES:
            os.makedirs(directory, exist_ok=True)
        
    def upload_image(self):
        image_file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if image_file_path:
            target_directory = IMG_DIR
            target_file_path = os.path.join(target_directory, os.path.basename(image_file_path))
            shutil.copy(image_file_path, target_file_path)
            
            caption = image_agent.image_to_text(image_file_path)
            
            message_html = f'<p style="background-color: lightblue;">Bot: {os.path.basename(image_file_path)} was added to image folder<br/>The caption is: {caption}</p><br/>'

            chatbot_gui.current_html += message_html
            chatbot_gui.text_area.set_html(chatbot_gui.current_html)

            chatbot_gui.conversation.append({
                "role": "assistant",
                "content": f'Bot: Image: {os.path.basename(image_file_path)} was added to image folder\nThe capition is: {caption}\n',  # directly add function response to the conversation
            })
            
    def upload_csv(self):
        csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if csv_file_path:
            target_directory = CSV_DIR
            target_file_path = os.path.join(target_directory, os.path.basename(csv_file_path))
            shutil.copy(csv_file_path, target_file_path)
            
            columns = csv_agent.read_csv_columns(csv_file_path)

            chatbot_gui.text_area.insert(tk.INSERT, f'{columns}\n', "bot")
            chatbot_gui.conversation.append({
                "role": "assistant",
                "content": f'Bot: {os.path.basename(csv_file_path)} was added to CSV folder\nThe columns are: {columns}\n',  # directly add function response to the conversation
            })

class AIManager:
    def run_chat(self, event=None):
        user_input = chatbot_gui.user_input_text.get("1.0", tk.END).strip()
        html = markdown.markdown(user_input)
        user_input_html = f'<p style="background-color: lightgray;">You: {html}</p><br/>'

        chatbot_gui.current_html += user_input_html
        chatbot_gui.text_area.set_html(chatbot_gui.current_html)

        chatbot_gui.user_input_text.delete("1.0", tk.END)

        chatbot_gui.is_loading = True
        chatbot_gui.loading_label = tk.Label(chatbot_gui.root, text="Loading...", bg="white", font=("Arial", 30))
        chatbot_gui.loading_label.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")  # Place the loading label over the application window
    
        self.handle_model_response(user_input)

    def handle_model_response(self, user_input):
        try:
            response, _ = run_conversation(user_input, chatbot_gui.conversation)
        except requests.exceptions.RequestException as e:  
            response = "Oops! A network error occurred, please try again later."
            print(e)
        except Exception as e:
            response = f"Oops! An error occurred: {str(e)}"

        chatbot_gui.root.after(0, chatbot_gui.update_text_area, response)
        chatbot_gui.text_area.see("end")  # Scrolls to the end of the text_area


class ChatbotGUI:
    def __init__(self):
        self.styles = Styles()
        self.file_manager = FileManager()
        self.ai_manager = AIManager()
        
        
        # Agents
        self.image_agent = ImageAgent()
        self.csv_agent = CSVHandler()
        self.file_write_agent = FileWriter()
        self.help_agent = HelpAgent()
        self.history_agent = HistoryHandler()
        self.kb_agent = KnowledgebaseHandler()
        self.scrape_agent = Scraper()
        self.wikidata_agent = WikidataAgent()
        self.python_agent = PythonRepl()
        
        # Initialize Pinecone
        #pinecone.init()

        # Create the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)

        # Create notebook (tab control)
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=0, rowspan=2, columnspan=2, sticky='nsew')

        # Create Tab 1
        self.chat_window = ttk.Frame(self.tabControl)
        self.tabControl.add(self.chat_window, text='Chat')
        self.create_widgets_chat_window()
        
        # Create Tab 2
        self.file_manager = ttk.Frame(self.tabControl)
        self.tabControl.add(self.file_manager, text='KnowledgeBase')
        self.create_widgets_file_manager()
        
        # Create Tab 3
        self.settings = ttk.Frame(self.tabControl)
        self.tabControl.add(self.settings, text='Settings')
        self.create_widgets_settings()

        self.is_loading = False
    
    def create_widgets_chat_window(self):
        self.chat_window.grid_rowconfigure(0, weight=1)  
        self.chat_window.grid_columnconfigure(0, weight=1)  
        self.chat_window.grid_columnconfigure(1, weight=0)  
        self.chat_window.grid_columnconfigure(2, weight=4)  
        ttk.Label(self.chat_window, text ="Chatbot").grid(column = 0, row = 0, padx = 30, pady = 30, sticky='nsew') 
        self.create_chat_sidebar(self.chat_window)
        self.create_chat_main(self.chat_window)

        # bind 'Enter' to run_chat function in Tab 1 only
        self.chat_window.bind('<Return>', self.ai_manager.run_chat)
    
    def create_chat_sidebar(self, parent):
        self.sidebar = ttk.Frame(parent, width=200)
        self.sidebar.grid(row=0, column=0, sticky='nsew')

        # Add a widget to make the sidebar visible. Adjust as necessary for your design.
        sidebar_label = ttk.Label(self.sidebar, text="Sidebar")
        sidebar_label.pack()
        
        
        # Add a reset button
        reset_button = ttk.Button(self.sidebar, text='Reset Conversation', command=self.reset_conversation, style='TButton')
        reset_button.pack()
        
        # Add an image upload button
        upload_button = ttk.Button(self.sidebar, text='Upload Image', command=self.file_manager.upload_image, style='TButton')
        upload_button.pack()
        
        # Add a csv upload button
        upload_csv_button = ttk.Button(self.sidebar, text='Upload CSV', command=self.file_manager.upload_csv, style='TButton')
        upload_csv_button.pack()
        
        # Add a theme dropdown
        available_themes = self.root.get_themes()  # get the list of themes
        self.theme_var = tk.StringVar()  # create a StringVar to hold selected theme
        self.theme_var.set(self.root.set_theme)  # set initial value to the current theme
        theme_dropdown = ttk.Combobox(self.sidebar, textvariable=self.theme_var, values=available_themes)
        theme_dropdown.pack(side=tk.BOTTOM, anchor='s')
        theme_dropdown.bind('<<ComboboxSelected>>', self.styles.change_theme)  # bind the selection event to the change_theme method
    
    def create_chat_main(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=0, column=2, sticky=N+S+E+W)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.create_text_area(main_frame)
        self.create_input_area(main_frame)

    def create_text_area(self, frame):
        self.text_area = HTMLLabel(frame, html="<p>Welcome to the chat!</p>", background="oldlace", font=('Ubuntu', 16))
        self.text_area.grid(row=0, column=0, sticky='nsew')
        self.current_html = "<p>Welcome to the chat!</p>"  # Initialize with the same content as the label

    def create_input_area(self, frame):
        bottom_frame = ttk.Frame(frame)
        bottom_frame.grid(sticky='nsew')

        self.user_input_text = scrolledtext.ScrolledText(bottom_frame, wrap='word', background="oldlace", height=2, font=('Ubuntu', 16)) # Set the font size and height
        self.user_input_text.grid(row=0, column=0, sticky='nsew')

        send_button = ttk.Button(bottom_frame, text='Send', command=self.ai_manager.run_chat, style='TButton')
        send_button.grid(row=0, column=1)

        bottom_frame.grid_columnconfigure(0, weight=1)
        
    def update_text_area(self, response):
        # Stop the loading animation
        html = markdown.markdown(response)
        self.is_loading = False
        self.loading_label.grid_remove()  # Remove the loading label from the application window
        # Create HTML for the response
        response_html = f'<p style="background-color: lightblue;">Bot: {html}</p><br/>'

        # Append the new message to the existing HTML content and update the widget
        self.current_html += response_html
        self.text_area.set_html(self.current_html)


    def reset_conversation(self):
        self.conversation = []
        reset_html = "<p>Conversation reset.</p>"
        self.text_area.set_html(reset_html)
        self.current_html = reset_html
    
    # TAB 2
    def create_widgets_file_manager(self):
        self.file_manager.grid_rowconfigure(0, weight=1)  
        self.file_manager.grid_columnconfigure(0, weight=1)  
        self.file_manager.grid_columnconfigure(1, weight=0)  
        self.file_manager.grid_columnconfigure(2, weight=4)  

        ttk.Label(self.file_manager, text ="Files").grid(column = 0, row = 0, padx = 30, pady = 30, sticky='nsew') 
        self.create_file_manager_sidebar(self.file_manager)
        self.create_file_manager_main(self.file_manager)
        self.refresh_folders_button = ttk.Button(self.file_manager, text="Refresh", command=self.file_manager_refresh_files)
        self.refresh_folders_button.grid(row=1, column=0, sticky=E)
        self.add_to_chat_button = ttk.Button(self.file_manager, text="Add to Chat History", command=self.file_manager_add_to_chat_history)
        self.add_to_chat_button.grid(row=2, column=0, sticky=E)
    
    def create_file_manager_sidebar(self, parent):
        self.tree = ttk.Treeview(parent)
        self.tree.grid(row=0, column=0, sticky=N+S+E+W)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=N+S)
        self.tree.config(yscrollcommand=scrollbar.set)

        # Add directories to tree
        for directory in DIRECTORIES:
            root = self.tree.insert('', 'end', text=directory, open=True)
            self.process_directory(root, directory)

        # Add event handler for selecting an item
        self.tree.bind('<<TreeviewSelect>>', self.file_manager_on_file_select)

        # Add event handler for opening a directory
        self.tree.bind('<<TreeviewOpen>>', self.file_manager_on_directory_open)

    def process_directory(self, parent, path):
        # Get all sub directories and files
        for p in os.scandir(path):
            # If file, add file
            if p.is_file():
                # Add only supported files
                if p.name.endswith(('.ts', '.txt', '.csv', '.py', '.js', '.rs', '.c', '.cpp', '.java', '.cs', '.rb', '.php', '.swift', '.go', '.lua', '.groovy', '.kotlin', '.dart', '.f', '.f90', '.f95', '.f03', '.f08', '.for', '.h', '.hh', '.hpp', '.hxx', '.pl', '.asm', '.sh', '.bat', '.html', '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml', '.sql', '.md', '.markdown', '.r', '.Rmd', '.m', '.mm', '.p', '.pas', '.pli', '.pl1', '.cob', '.cbl', '.j', '.jl', '.erl', '.hs', '.elm', '.scala', '.sc', '.clj', '.cljs', '.edn', '.coffee', '.kt', '.hx', '.pde', '.ino', '.cls', '.bas', '.frm', '.vba', '.vbs', '.d', '.ada', '.adb', '.ads', '.ml', '.mli', '.fs', '.fsi', '.fsx', '.v', '.vh', '.vhd', '.vhdl', '.tex', '.sty', '.cls', '.clojure', '.png', '.jpg', '.jpeg')):
                    self.tree.insert(parent, 'end', text=p.name)


    def create_file_manager_main(self, parent):
        self.viewer_frame = ttk.Frame(parent)
        self.viewer_frame.grid(row=0, column=2, sticky=N+S+E+W)
        
        self.md_viewer = HTMLLabel(self.viewer_frame, html="<h1>Select a file from the list</h1>")
        self.md_viewer.pack(fill='both', expand=True)
        
        # Create a label for images
        self.image_label = ttk.Label(self.viewer_frame)
        self.image_label.pack(fill='both', expand=True)

    def file_manager_on_file_select(self, evt):
        # Get selected file name
        selected_item_id = self.tree.selection()[0]
        file_name = self.tree.item(selected_item_id, 'text')
        
        file_path = self.file_manager_get_full_path(selected_item_id)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            # Read the file
            if file_name.endswith('.md'):
                with open(file_path, 'r') as f:
                    file_content = f.read()
                html = markdown.markdown(file_content)
                self.md_viewer.set_html(html)
                self.md_viewer.pack(fill='both', expand=True)  # Make sure it's visible
                self.image_label.pack_forget()  # Hide the image label
            elif file_name.endswith(('.ts', 'txt', 'csv', '.py', '.js', '.rs', '.c', '.cpp', '.java', '.cs', '.rb', '.php', '.swift', '.go', '.lua', '.groovy', '.kotlin', '.dart', '.f', '.f90', '.f95', '.f03', '.f08', '.for', '.h', '.hh', '.hpp', '.hxx', '.pl', '.asm', '.sh', '.bat', '.html', '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml', '.sql', '.md', '.markdown', '.r', '.Rmd', '.m', '.mm', '.p', '.pas', '.pli', '.pl1', '.cob', '.cbl', '.j', '.jl', '.erl', '.hs', '.elm', '.scala', '.sc', '.clj', '.cljs', '.edn', '.coffee', '.kt', '.hx', '.pde', '.ino', '.cls', '.bas', '.frm', '.vba', '.vbs', '.d', '.ada', '.adb', '.ads', '.ml', '.mli', '.fs', '.fsi', '.fsx', '.v', '.vh', '.vhd', '.vhdl', '.tex', '.sty', '.cls', '.clojure')):
                with open(file_path, 'r') as f:
                    file_content = f.read()
                html = '<pre>{}</pre>'.format(file_content)
                self.md_viewer.set_html(html)
                self.md_viewer.pack(fill='both', expand=True)  # Make sure it's visible
                self.image_label.pack_forget()  # Hide the image label
            elif file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(file_path)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Keep a reference to prevent garbage collection
                self.image_label.pack(fill='both', expand=True)  # Make sure it's visible
                self.md_viewer.pack_forget()  # Hide the HTMLLabel
            else:
                html = '<p>Unsupported file type</p>'
                self.md_viewer.set_html(html)
                self.md_viewer.pack(fill='both', expand=True)  # Make sure it's visible
                self.image_label.pack_forget()  # Hide the image label

    def file_manager_get_full_path(self, item_id):
        parent_id = self.tree.parent(item_id)
        if parent_id:  # if item has a parent
            return os.path.join(self.file_manager_get_full_path(parent_id), self.tree.item(item_id, 'text'))
        else:  # if item has no parent
            return self.tree.item(item_id, 'text')

    def file_manager_on_directory_open(self, event):
        # Get the directory that's being opened
        directory_id = self.tree.focus()

        # Delete the old contents of the directory
        for child_id in self.tree.get_children(directory_id):
            self.tree.delete(child_id)

        # Populate the directory with its subdirectories and files
        directory_path = self.file_manager_get_full_path(directory_id)
        self.process_directory(directory_id, directory_path)
    
    def file_manager_refresh_files(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        # List of directories
        directories = DIRECTORIES

        # Refresh directories
        for directory in directories:
            root = self.tree.insert('', 'end', text=directory, open=True)
            self.process_directory(root, directory)

    def file_manager_add_to_chat_history(self):
        # Get the currently selected file
        selected_item_id = self.tree.selection()[0]
        selected_file = self.tree.item(selected_item_id, 'text')

        file_path = self.file_manager_get_full_path(selected_item_id)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            # If csv file, get columns
            if file_path.endswith('.csv'):
                columns = csv_agent.read_csv_columns(file_path)
                self.conversation.append({
                    "role": "user",
                    "content": f'Columns: {columns}\n',
                })

                # Convert the column list to HTML format
                columns_html = columns.replace('- ', '<li>').replace('\n', '</li>')
                columns_html = f'<ul>{columns_html}</li></ul>'

                content_html = f'<p style="background-color: lightgray;">You: <br/>{columns_html}</p><br/>'
                self.current_html += content_html
                self.text_area.set_html(self.current_html)
                return
            # If image file, say no
            elif file_path.endswith(('.png', '.jpg', '.jpeg')):
                logging.info('Image not supported')
                return

            # Open and read the file
            with open(file_path, 'r') as file:
                content = file.read()

            # Append to chat history
            self.conversation.append({
                "role": "user",
                "content": f'{content}\n',
            })

            # Create HTML for the loaded content and append to the current HTML
            content_html = f'<p style="background-color: lightgray;">You: Content loaded:<br/>{content}</p><br/>'
            self.current_html += content_html
            self.text_area.set_html(self.current_html)

            # You may want to automatically scroll to the end of the text area
            self.text_area.see('end')

        
    def create_widgets_settings(self):
        self.settings.grid_rowconfigure(0, weight=1)
        self.settings.grid_columnconfigure(0, weight=1)
        self.settings.grid_columnconfigure(1, weight=0)
        self.settings.grid_columnconfigure(2, weight=4)
        
        ttk.Label(self.settings, text="Agent Configuration", justify=CENTER).grid(column=0, row=0, padx=30, pady=30, sticky='nsew')
        self.create_settings_main(self.settings)
        self.create_settings_sidebar(self.settings)

    def create_settings_sidebar(self, parent):
        self.sidebar_settings = ttk.Frame(parent, width=200)
        self.sidebar_settings.grid(row=0, column=0, sticky='nsew')

        sidebar_label = ttk.Label(self.sidebar_settings, text="Settings")
        sidebar_label.pack()
        
        # Get agents from the agents folder
        agents_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "agents")  # Directory of agents
        agents = [f[:-3] for f in os.listdir(agents_dir) if f.endswith('.py') and f != "__init__.py" and f != "function_call_agent.py"]  # Remove '.py' from file name

        
        self.agent_select = ttk.Combobox(self.sidebar_settings, values=agents)
        self.agent_select.set('Select Agent')  # Default text
        self.agent_select.pack(pady=10)  # Add some padding around the combobox
        self.agent_select.bind("<<ComboboxSelected>>", self.on_agent_selected)  # Bind the on_agent_selected function to the combobox


    def update_temperature(self, value):
        rounded_value = round(float(value) * 10) / 10
        self.temperature_scale.set(rounded_value)
        self.temperature_var.set(str(rounded_value))

    def update_top_p(self, value):
        rounded_value = round(float(value) * 10) / 10
        self.top_p_scale.set(rounded_value)
        self.top_p_var.set(str(rounded_value))

    def update_frequency_penalty(self, value):
        rounded_value = round(float(value) * 10) / 10
        self.frequency_penalty_scale.set(rounded_value)
        self.frequency_penalty_var.set(str(rounded_value))

    def update_presence_penalty(self, value):
        rounded_value = round(float(value) * 10) / 10
        self.presence_penalty_scale.set(rounded_value)
        self.presence_penalty_var.set(str(rounded_value))

    def create_settings_main(self, parent):
        config_frame = ttk.Frame(parent)
        config_frame.grid(row=1, column=0, sticky='nsew')
        

        # Create StringVar objects for the sliders
        self.temperature_var = StringVar(value=self.csv_agent.temperature)
        self.top_p_var = StringVar(value=self.csv_agent.top_p)
        self.frequency_penalty_var = StringVar(value=self.csv_agent.frequency_penalty)
        self.presence_penalty_var = StringVar(value=self.csv_agent.presence_penalty)

        # For Model
        ttk.Label(config_frame, text="Model", anchor='e').grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.model_entry = ttk.Entry(config_frame)
        self.model_entry.insert(0, self.csv_agent.model)  # Set from CSVHandler
        self.model_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        
        # For Temperature
        ttk.Label(config_frame, text="Temperature", anchor='e').grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.temperature_label = ttk.Label(config_frame, textvariable=self.temperature_var) # Create a label with textvariable
        self.temperature_label.grid(row=1, column=1, padx=5, pady=5, sticky='n')
        self.temperature_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.temperature_var)
        self.temperature_scale.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # For Top_p
        ttk.Label(config_frame, text="Top_p", anchor='e').grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        self.top_p_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.top_p_var)
        self.top_p_label = ttk.Label(config_frame, textvariable=self.top_p_var)
        self.top_p_label.grid(row=3, column=1, padx=5, pady=5, sticky='n')
        self.top_p_scale.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # For Frequency Penalty
        ttk.Label(config_frame, text="Frequency Penalty", anchor='e').grid(row=5, column=0, padx=5, pady=5, sticky='ew')
        self.frequency_penalty_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.frequency_penalty_var)
        self.frequency_penalty_label = ttk.Label(config_frame, textvariable=self.frequency_penalty_var)
        self.frequency_penalty_label.grid(row=5, column=1, padx=5, pady=5, sticky='n')
        self.frequency_penalty_scale.grid(row=6, column=1, padx=5, pady=5, sticky='ew')


        # For Presence Penalty
        ttk.Label(config_frame, text="Presence Penalty", anchor='e').grid(row=7, column=0, padx=5, pady=5, sticky='ew')
        self.presence_penalty_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.presence_penalty_var)
        self.presence_penalty_label = ttk.Label(config_frame, textvariable=self.presence_penalty_var)
        self.presence_penalty_label.grid(row=7, column=1, padx=5, pady=5, sticky='n')
        self.presence_penalty_scale.grid(row=8, column=1, padx=5, pady=5, sticky='ew')

        # Button to apply changes
        apply_button = ttk.Button(config_frame, text='Apply', command=self.update_agent_settings)
        apply_button.grid(row=9, column=1, padx=5, pady=5, sticky='ew')

    def on_agent_selected(self, event):
        selected_agent = self.agent_select.get()
        self.agent = getattr(self, selected_agent)

        # Update the settings
        self.update_settings_from_agent()

    def update_settings_from_agent(self):
        self.model_entry.delete(0, 'end')
        self.model_entry.insert(0, self.agent.model)
        self.temperature_var.set(self.agent.temperature)
        self.top_p_var.set(self.agent.top_p)
        self.frequency_penalty_var.set(self.agent.frequency_penalty)
        self.presence_penalty_var.set(self.agent.presence_penalty)

    def update_agent_settings(self):
        self.agent.model = self.model_entry.get() or "gpt-4-0613"
        self.agent.temperature = float(self.temperature_var.get() or 0.3)
        self.agent.top_p = float(self.top_p_var.get() or 1.0)
        self.agent.frequency_penalty = float(self.frequency_penalty_var.get() or 0.0)
        self.agent.presence_penalty = float(self.presence_penalty_var.get() or 0.0)


    

    def run(self):
        # logic to create and manage tkinter root, e.g., root = tk.Tk()
        # and then...
        self.root.mainloop()

if __name__ == "__main__":
    chatbot_gui = ChatbotGUI()
    chatbot_gui.run()