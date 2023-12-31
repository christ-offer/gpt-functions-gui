import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkhtmlview import HTMLLabel
import markdown
from PIL import Image, ImageTk
import fitz
import logging
import os

from agents.image_agent import ImageAgent
from agents.csv_agent import CSVHandler

from gui.chat_tab import ChatTab

from constants import *
DIRECTORIES = [
    KB_DIR, 
    HISTORY_DIR, 
    CSV_DIR, 
    IMG_DIR, 
    CODE_DIR, 
    LOG_DIR, 
    DATA_DIR, 
    PROJECTS_DIR
    ]


class FileTab:
    def __init__(self, parent, file_tab):
        self.root = parent
        self.parent = parent
        self.image_agent = ImageAgent()
        self.csv_agent = CSVHandler()
        self.file_tab = file_tab
        self.chat_tab = ChatTab(parent=self.root, chat_window=self.root.chat_window)
        self.create_widgets_file_manager()

    def create_widgets_file_manager(self):
        self.file_tab.grid_rowconfigure(0, weight=1)  
        self.file_tab.grid_columnconfigure(0, weight=0)  
        self.file_tab.grid_columnconfigure(1, weight=0)  
        self.file_tab.grid_columnconfigure(2, weight=4)  

        ttk.Label(self.file_tab, text ="Files").grid(column = 0, row = 0, padx = 30, pady = 30, sticky='nsew') 
        self.create_file_tab_sidebar(self.file_tab)
        self.create_file_tab_main(self.file_tab)
        self.refresh_folders_button = ttk.Button(self.file_tab, text="Refresh", command=self.file_tab_refresh_files)
        self.refresh_folders_button.grid(row=1, column=0, sticky=E)
        self.add_to_chat_button = ttk.Button(self.file_tab, text="Add to Chat History", command=self.file_tab_add_to_chat_history)
        self.add_to_chat_button.grid(row=2, column=0, sticky=E)

    def create_file_tab_sidebar(self, parent):
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
        self.tree.bind('<<TreeviewSelect>>', self.file_tab_on_file_select)

        # Add event handler for opening a directory
        self.tree.bind('<<TreeviewOpen>>', self.file_tab_on_directory_open)

    def process_directory(self, parent, path):
        # Get all sub directories and files
        for p in os.scandir(path):
            # If file, add file
            if p.is_file():
                # Add only supported files
                if p.name.endswith(('.ts', '.txt', 'pdf', '.csv', '.py', '.js', '.rs', '.c', '.cpp', '.java', '.cs', '.rb', '.php', '.swift', '.go', '.lua', '.groovy', '.kotlin', '.dart', '.f', '.f90', '.f95', '.f03', '.f08', '.for', '.h', '.hh', '.hpp', '.hxx', '.pl', '.asm', '.sh', '.bat', '.html', '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml', '.sql', '.md', '.markdown', '.r', '.Rmd', '.m', '.mm', '.p', '.pas', '.pli', '.pl1', '.cob', '.cbl', '.j', '.jl', '.erl', '.hs', '.elm', '.scala', '.sc', '.clj', '.cljs', '.edn', '.coffee', '.kt', '.hx', '.pde', '.ino', '.cls', '.bas', '.frm', '.vba', '.vbs', '.d', '.ada', '.adb', '.ads', '.ml', '.mli', '.fs', '.fsi', '.fsx', '.v', '.vh', '.vhd', '.vhdl', '.tex', '.sty', '.cls', '.clojure', '.png', '.jpg', '.jpeg')):
                    self.tree.insert(parent, 'end', text=p.name)

    def create_file_tab_main(self, parent):
        self.viewer_frame = ttk.Frame(parent)
        self.viewer_frame.grid(row=0, column=2, sticky=N+S+E+W)
        
        self.md_viewer = HTMLLabel(self.viewer_frame, html="<h1>Select a file from the list</h1>")
        self.md_viewer.pack(fill='both', expand=True)
        
        # Create a label for images
        self.image_label = ttk.Label(self.viewer_frame)
        self.image_label.pack(fill='both', expand=True)

    def file_tab_on_file_select(self, evt):
        # Get selected file name
        selected_item_id = self.tree.selection()[0]
        file_name = self.tree.item(selected_item_id, 'text')
        
        file_path = self.file_tab_get_full_path(selected_item_id)

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
            elif file_name.lower().endswith('.pdf'):  # Add support for PDF
                doc = fitz.open(file_path)
                page = doc.load_page(0)  # number of page
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                raw = pix.samples  # get the raw pixel data
                image = Image.frombytes("RGB", [pix.width, pix.height], raw)
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

    def file_tab_get_full_path(self, item_id):
        parent_id = self.tree.parent(item_id)
        if parent_id:  # if item has a parent
            return os.path.join(self.file_tab_get_full_path(parent_id), self.tree.item(item_id, 'text'))
        else:  # if item has no parent
            return self.tree.item(item_id, 'text')

    def file_tab_on_directory_open(self, event):
        # Get the directory that's being opened
        directory_id = self.tree.focus()

        # Delete the old contents of the directory
        for child_id in self.tree.get_children(directory_id):
            self.tree.delete(child_id)

        # Populate the directory with its subdirectories and files
        directory_path = self.file_tab_get_full_path(directory_id)
        self.process_directory(directory_id, directory_path)

    def file_tab_refresh_files(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        # List of directories
        directories = DIRECTORIES

        # Refresh directories
        for directory in directories:
            root = self.tree.insert('', 'end', text=directory, open=True)
            self.process_directory(root, directory)

    def file_tab_add_to_chat_history(self):
        # Get the currently selected file
        selected_item_id = self.tree.selection()[0]
        #selected_file = self.tree.item(selected_item_id, 'text')

        file_path = self.file_tab_get_full_path(selected_item_id)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            # If csv file, get columns
            if file_path.endswith('.csv'):
                columns = self.csv_agent.read_csv_columns(file_path)
                self.chat_tab.conversation.append({
                    "role": "user",
                    "content": f'Columns: {columns}\n',
                })

                # Convert the column list to HTML format
                columns_html = columns.replace('- ', '<li>').replace('\n', '</li>')
                columns_html = f'<ul>{columns_html}</li></ul>'

                content_html = f'<p style="background-color: lightgray;">You: <br/>{columns_html}</p><br/>'
                self.chat_tab.current_html += content_html
                self.chat_tab.text_area.set_html(self.current_html)
                return
            # If image file, say no
            elif file_path.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                logging.info('Image not supported')
                return

            # Open and read the file
            with open(file_path, 'r') as file:
                content = file.read()

            # Append to chat history
            self.chat_tab.conversation.append({
                "role": "user",
                "content": f'{content}\n',
            })

            # Create HTML for the loaded content and append to the current HTML
            # Here, newlines are replaced with <br/> for proper HTML formatting
            content_html = f'<p style="background-color: lightgray;">You: Content loaded from {file_path}:<br/>'
            with open(file_path, 'r') as file:
                for i, line in enumerate(file, start=1):
                    # Append to chat history with line numbers
                    # Add line numbers to the HTML content
                    content_html += f'{i}: {line}<br/>'
            self.chat_tab.current_html += content_html
            self.chat_tab.text_area.set_html(self.chat_tab.current_html)

            # You may want to automatically scroll to the end of the text area
            self.chat_tab.text_area.see('end')
