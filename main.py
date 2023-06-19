import logging
import tkinter as tk
from tkinter import scrolledtext
from ttkthemes import ThemedTk
from tkinter import ttk
import os
import threading
from tkinter import filedialog
import shutil
from PIL import Image, ImageTk

from chatbot import run_conversation
from functions import function_params, wikidata_sparql_query, scrape_webpage, write_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns, image_to_text, read_file, edit_file, list_history_entries, write_history_entry, read_history_entry, query_wolframalpha

conversation = []

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# GUI
class ChatbotGUI:
    def __init__(self):
        self.root = ThemedTk(theme="black") # Choose a suitable theme
        self.root.title('Personal Assistant')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)  # Give sidebar and main frame different weight
        self.root.grid_columnconfigure(1, weight=4)
        self.conversation = []  # Add this line
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Ubuntu', 14))
        self.create_widgets()
        
        self.is_loading = False

    def create_widgets(self):
        self.create_sidebar()
        self.create_main_area()
        self.root.bind('<Return>', self.run_chat)  # If you press 'Enter', it will trigger the run_chat function

    def create_sidebar(self):
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky='nsew')

        # Add a widget to make the sidebar visible. Adjust as necessary for your design.
        sidebar_label = ttk.Label(self.sidebar, text="Sidebar")
        sidebar_label.pack()
        
        # Add a settings button
        settings_button = ttk.Button(self.sidebar, text='Settings', command=self.open_settings)
        settings_button.pack()
        
        # Add a reset button
        reset_button = ttk.Button(self.sidebar, text='Reset Conversation', command=self.reset_conversation, style='TButton')
        reset_button.pack()
        
        # Add an image upload button
        upload_button = ttk.Button(self.sidebar, text='Upload Image', command=self.upload_image, style='TButton')
        upload_button.pack()
        
        # Add a csv upload button
        upload_csv_button = ttk.Button(self.sidebar, text='Upload CSV', command=self.upload_csv, style='TButton')
        upload_csv_button.pack()
        
        # Add a theme dropdown
        available_themes = self.root.get_themes()  # get the list of themes
        self.theme_var = tk.StringVar()  # create a StringVar to hold selected theme
        self.theme_var.set(self.root.set_theme)  # set initial value to the current theme
        theme_dropdown = ttk.Combobox(self.sidebar, textvariable=self.theme_var, values=available_themes)
        theme_dropdown.pack(side=tk.BOTTOM, anchor='s')
        theme_dropdown.bind('<<ComboboxSelected>>', self.change_theme)  # bind the selection event to the change_theme method

    def open_settings(self):
        # Create a new settings window
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title('Settings')
        self.settings_window.geometry('400x200')  # Adjust the size as needed

        # Create a container for the settings
        settings_frame = ttk.Frame(self.settings_window)
        settings_frame.pack(pady=10, padx=10)

        # Add an entry for OPENAI_API_KEY
        api_key_label = ttk.Label(settings_frame, text="OPENAI_API_KEY")
        api_key_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(settings_frame, textvariable=self.api_key_var, font=('Arial', 18))  # Adjust the font size as needed
        api_key_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Add a save button to apply changes
        save_button = ttk.Button(settings_frame, text='Save', command=self.apply_settings)
        save_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)

    def apply_settings(self):
        # Export OPENAI_API_KEY as an environment variable
        os.environ['OPENAI_API_KEY'] = self.api_key_var.get()

        # Inform the user that changes have been applied
        #messagebox.showinfo("Settings", "Settings have been applied successfully.")

        # Close the settings window
        self.settings_window.destroy()
        
        
    def upload_image(self):
        image_file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if image_file_path:
            target_directory = "data/images"
            os.makedirs(target_directory, exist_ok=True)
            target_file_path = os.path.join(target_directory, os.path.basename(image_file_path))
            shutil.copy(image_file_path, target_file_path)
            
            caption = image_to_text(image_file_path)
            
            # Load image
            img = Image.open(image_file_path)
            img.thumbnail((500,500)) # Limit the size of the image to 200x200 pixels
            img = ImageTk.PhotoImage(img)
            image_label = tk.Label(image=img) # Create a label to hold the image
            image_label.image = img # Keep a reference to the image to prevent it from being garbage collected

            # Add image to text area
            self.text_area.window_create(tk.END, window=image_label)
            self.text_area.insert(tk.END, '\n')
            
            # Insert message into text area
            self.text_area.insert(tk.INSERT, f'Bot: {os.path.basename(image_file_path)} was added to image folder\n The caption is: {caption}\n', "bot")
            
            self.conversation.append({
                "role": "assistant",
                "content": f'Bot: {os.path.basename(image_file_path)} was added to image folder\nThe capition is: {caption}\n',  # directly add function response to the conversation
            })

    def upload_csv(self):
        csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if csv_file_path:
            target_directory = "data/csv"
            os.makedirs(target_directory, exist_ok=True)
            target_file_path = os.path.join(target_directory, os.path.basename(csv_file_path))
            shutil.copy(csv_file_path, target_file_path)
            
            columns = read_csv_columns(csv_file_path)

            # Insert message into text area
            self.text_area.insert(tk.INSERT, f'Bot: {os.path.basename(csv_file_path)} was added to CSV folder\nThe columns are: {columns}\n', "bot")
            # add same text to conversation
            self.conversation.append({
                "role": "assistant",
                "content": f'Bot: {os.path.basename(csv_file_path)} was added to CSV folder\nThe columns are: {columns}\n',  # directly add function response to the conversation
            })



    def create_main_area(self):
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=1, sticky='nsew')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.create_text_area(main_frame)
        self.create_input_area(main_frame)

    def create_text_area(self, frame):
        self.text_area = scrolledtext.ScrolledText(frame, wrap='word', background="oldlace", font=('Ubuntu', 16))
        self.text_area.tag_configure("user", background="lightgray", spacing1=30, spacing3=10)  # style for user text
        self.text_area.tag_configure("bot", background="lightblue", spacing1=30, spacing3=10)  # style for bot text
        self.text_area.grid(row=0, column=0, sticky='nsew')

    def create_input_area(self, frame):
        bottom_frame = ttk.Frame(frame)
        bottom_frame.grid(sticky='nsew')

        self.user_input_text = scrolledtext.ScrolledText(bottom_frame, wrap='word', background="oldlace", height=2, font=('Ubuntu', 16)) # Set the font size and height
        self.user_input_text.grid(row=0, column=0, sticky='nsew')

        send_button = ttk.Button(bottom_frame, text='Send', command=self.run_chat, style='TButton')
        send_button.grid(row=0, column=1)

        bottom_frame.grid_columnconfigure(0, weight=1)
    
    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.root.set_theme(selected_theme)
    
    def run_chat(self, event=None):
        user_input = self.user_input_text.get("1.0", tk.END).strip()
        self.text_area.insert(tk.INSERT, f'You: {user_input}\n', "user")
        self.user_input_text.delete("1.0", tk.END)

        # Start the loading animation
        self.is_loading = True
        self.loading_label = tk.Label(self.root, text="Loading...", bg="white", font=("Arial", 30))
        self.loading_label.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")  # Place the loading label over the application window

        # Start a new thread to run the model and handle the response
        threading.Thread(target=self.handle_model_response, args=(user_input,)).start()

    def handle_model_response(self, user_input):
        try:
            response, _ = run_conversation(user_input, self.conversation)
        except Exception as e:
            response = f"Error: {str(e)}"

        # Update the text area with the response
        # Because we are updating the UI from a different thread, we must use the 'after' method
        self.root.after(0, self.update_text_area, response)

    def update_text_area(self, response):
        # Stop the loading animation
        self.is_loading = False
        self.loading_label.grid_remove()  # Remove the loading label from the application window

        self.text_area.insert(tk.INSERT, f'Bot: {response}\n', "bot")

    


    def reset_conversation(self):
        self.conversation = []
        self.text_area.delete('1.0', tk.END)

    def run(self):
        self.root.mainloop()



if __name__ == "__main__":
    chatbot_gui = ChatbotGUI()
    chatbot_gui.run()