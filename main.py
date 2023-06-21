import os
import logging
import requests
import shutil
import markdown
import tkinter as tk
from tkinter import ttk, Listbox, Scrollbar, N, S, E, W, scrolledtext, filedialog, Canvas
from ttkthemes import ThemedTk
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk

from chatbot import run_conversation
from functions import image_to_text, read_csv_columns

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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
        ChatbotGUI.conversation = []  # Add this line
        ChatbotGUI.style = ttk.Style()
        ChatbotGUI.style.configure('TButton', font=('Ubuntu', 14))
        ChatbotGUI.md_directory = "kb/"  # Set path to markdown files
        ChatbotGUI.history_directory = "history/"  # Set path to markdown files
        ChatbotGUI.img_directory = "data/images/"  # Set path to image files
        ChatbotGUI.csv_directory = "data/csv/"  # Set path to csv files
        ChatbotGUI.root.option_add('*foreground', 'black')  # Setting default text color to black

    def apply_default_style(self, widget):
        widget.config(font=self.default_font, bg=self.default_bg_color, fg=self.default_fg_color)
    
    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.root.set_theme(selected_theme)

class FileManager:
    def __init__(self):
        # Check if directories exist and create them if they don't
        os.makedirs(ChatbotGUI.md_directory, exist_ok=True)
        os.makedirs(ChatbotGUI.img_directory, exist_ok=True)
        os.makedirs(ChatbotGUI.csv_directory, exist_ok=True)
        os.makedirs(ChatbotGUI.history_directory, exist_ok=True)
        
    def upload_image(self):
        image_file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if image_file_path:
            target_directory = "data/images"
            os.makedirs(target_directory, exist_ok=True)
            target_file_path = os.path.join(target_directory, os.path.basename(image_file_path))
            shutil.copy(image_file_path, target_file_path)
            
            caption = image_to_text(image_file_path)
            
            # Create HTML for the bot's message
            message_html = f'<p style="background-color: lightblue;">Bot: {os.path.basename(image_file_path)} was added to image folder<br/>The caption is: {caption}</p><br/>'

            # Append the new message to the existing HTML content and update the widget
            self.current_html += message_html
            self.text_area.set_html(self.current_html)

            chatbot_gui.conversation.append({
                "role": "assistant",
                "content": f'Bot: Image: {os.path.basename(image_file_path)} was added to image folder\nThe capition is: {caption}\n',  # directly add function response to the conversation
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
            chatbot_gui.text_area.insert(tk.INSERT, f'Bot: {os.path.basename(csv_file_path)} was added to CSV folder\nThe columns are: {columns}\n', "bot")
            # add same text to conversation
            chatbot_gui.conversation.append({
                "role": "assistant",
                "content": f'Bot: {os.path.basename(csv_file_path)} was added to CSV folder\nThe columns are: {columns}\n',  # directly add function response to the conversation
            })

class AIManager:
    def run_chat(self, event=None):
        user_input = chatbot_gui.user_input_text.get("1.0", tk.END).strip()
        html = markdown.markdown(user_input)
        # Create HTML for the user's input
        user_input_html = f'<p style="background-color: lightgray;">You: {html}</p><br/>'

        # Append the new message to the existing HTML content and update the widget
        chatbot_gui.current_html += user_input_html
        chatbot_gui.text_area.set_html(chatbot_gui.current_html)

        chatbot_gui.user_input_text.delete("1.0", tk.END)

        # Start the loading animation
        chatbot_gui.is_loading = True
        chatbot_gui.loading_label = tk.Label(chatbot_gui.root, text="Loading...", bg="white", font=("Arial", 30))
        chatbot_gui.loading_label.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")  # Place the loading label over the application window
    
        self.handle_model_response(user_input)
        
        # Start a new thread to run the model and handle the response
        #threading.Thread(target=self.handle_model_response, args=(user_input,)).start()

    def handle_model_response(self, user_input):
        try:
            response, _ = run_conversation(user_input, chatbot_gui.conversation)
        except requests.exceptions.RequestException as e:  
            response = "Oops! A network error occurred, please try again later."
            print(e)
        except Exception as e:
            response = f"Oops! An error occurred: {str(e)}"

        # Update the text area with the response
        # Because we are updating the UI from a different thread, we must use the 'after' method
        chatbot_gui.root.after(0, chatbot_gui.update_text_area, response)
        chatbot_gui.text_area.see("end")  # Scrolls to the end of the text_area

class SettingsManager:
    def open_settings(self):
        # Create a new settings window
        self.settings_window = tk.Toplevel(chatbot_gui.root)
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


class ChatbotGUI:
    def __init__(self):
        self.styles = Styles()
        self.file_manager = FileManager()
        self.ai_manager = AIManager()
        self.settings_manager = SettingsManager()

        # Create the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)

        # Create notebook (tab control)
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=0, rowspan=2, columnspan=2, sticky='nsew')

        # Create Tab 1
        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Chat')

        # Create widgets in Tab 1
        self.create_widgets_tab1()
        
        # Create Tab 2
        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text='KnowledgeBase')

        # Create widgets in Tab 2
        self.create_widgets_tab2()
        
        self.is_loading = False
        
        # Create Tab 3
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='History')
        
        # Create widgets in Tab 3
        self.create_widgets_tab3()
        
        # Tab 4
        self.tab4 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab4, text='Images')
        
        # Create widgets in Tab 4
        self.create_widgets_tab4()
    
    def create_widgets_tab1(self):
        self.tab1.grid_rowconfigure(0, weight=1)  # Add this line
        self.tab1.grid_columnconfigure(0, weight=1)  # Add this line
        self.tab1.grid_columnconfigure(1, weight=0)  # Add this line
        self.tab1.grid_columnconfigure(2, weight=4)  # Add this line
        ttk.Label(self.tab1, text ="Chatbot").grid(column = 0, row = 0, padx = 30, pady = 30, sticky='nsew')  # Add this parameter
        self.create_sidebar(self.tab1)
        self.create_main_area(self.tab1)

        # bind 'Enter' to run_chat function in Tab 1 only
        self.tab1.bind('<Return>', self.ai_manager.run_chat)

    def create_widgets_tab2(self):
        self.tab2.grid_rowconfigure(0, weight=1)  # Add this line
        self.tab2.grid_columnconfigure(0, weight=1)  # Add this line
        self.tab2.grid_columnconfigure(1, weight=0)  # Add this line
        self.tab2.grid_columnconfigure(2, weight=4)  # Add this line

        ttk.Label(self.tab2, text ="KnowledgeBase").grid(column = 0, 
                                                        row = 0, 
                                                        padx = 30, 
                                                        pady = 30, 
                                                        sticky='nsew')  # Add this parameter
        self.create_md_sidebar(self.tab2)
        self.create_md_viewer(self.tab2)
        self.refresh_md_button = ttk.Button(self.tab2, text="Refresh", command=self.refresh_files)
        self.refresh_md_button.grid(row=1, column=0, sticky=E)
        self.add_to_chat_button = ttk.Button(self.tab2, text="Add to Chat History", command=self.add_to_chat_history)
        self.add_to_chat_button.grid(row=2, column=0, sticky=E)
    
    def create_widgets_tab3(self):
        self.tab3.grid_rowconfigure(0, weight=1)
        self.tab3.grid_columnconfigure(0, weight=1)
        self.tab3.grid_columnconfigure(1, weight=0)
        self.tab3.grid_columnconfigure(2, weight=4)
        
        ttk.Label(self.tab3, text ="History").grid(column = 0,
                                                    row = 0,
                                                    padx = 30,
                                                    pady = 30,
                                                    sticky='nsew')
        self.create_history_sidebar(self.tab3)
        self.create_history_viewer(self.tab3)
        self.refresh_md_button = ttk.Button(self.tab3, text="Refresh", command=self.refresh_files)
        self.refresh_md_button.grid(row=1, column=0, sticky=E)
        self.add_to_chat_button = ttk.Button(self.tab3, text="Add to Chat History", command=self.add_to_chat_history)
        self.add_to_chat_button.grid(row=2, column=0, sticky=E)
    
    def create_widgets_tab4(self):
        self.tab4.grid_rowconfigure(0, weight=1)
        self.tab4.grid_columnconfigure(0, weight=1)
        self.tab4.grid_columnconfigure(1, weight=0)
        self.tab4.grid_columnconfigure(2, weight=4)
        
        ttk.Label(self.tab4, text ="Images").grid(column = 0,
                                                  row = 0,
                                                  padx = 30,
                                                  pady = 30,
                                                  sticky='nsew')
        self.create_img_sidebar(self.tab4)
        self.create_img_viewer(self.tab4)
        self.refresh_md_button = ttk.Button(self.tab4, text="Refresh", command=self.refresh_files)
        self.refresh_md_button.grid(row=1, column=0, sticky=E)
    
    def refresh_files(self):
          # Refresh Markdown files
          self.md_listbox.delete(0, 'end')
          self.update_md_files()
          self.md_listbox.update_idletasks()

          # Refresh Image files
          self.img_listbox.delete(0, 'end')
          self.update_img_files()
          self.img_listbox.update_idletasks()
          
          # Refresh History files
          self.history_listbox.delete(0, 'end')
          self.update_history_files()
          self.history_listbox.update_idletasks()

      
    def create_sidebar(self, parent):
        self.sidebar = ttk.Frame(parent, width=200)
        self.sidebar.grid(row=0, column=0, sticky='nsew')

        # Add a widget to make the sidebar visible. Adjust as necessary for your design.
        sidebar_label = ttk.Label(self.sidebar, text="Sidebar")
        sidebar_label.pack()
        
        # Add a settings button
        settings_button = ttk.Button(self.sidebar, text='Settings', command=self.settings_manager.open_settings)
        settings_button.pack()
        
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
    
    def create_main_area(self, parent):
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
    
    def create_md_sidebar(self, parent):
        self.md_listbox = Listbox(parent)
        self.md_listbox.grid(row=0, 
                            column=0, 
                            sticky=N+S+E+W)  # Add these parameters

        scrollbar = Scrollbar(parent, orient="vertical", command=self.md_listbox.yview)
        scrollbar.grid(row=0, 
                      column=1, 
                      sticky=N+S)  
        self.md_listbox.config(yscrollcommand=scrollbar.set)

        # Load the list of markdown files
        self.update_md_files()

        # Add event handler for selecting an item
        self.md_listbox.bind('<<ListboxSelect>>', self.on_md_file_select)

    def create_md_viewer(self, parent):
        self.md_viewer = HTMLLabel(parent, html="<h1>Select a file from the list</h1>")
        self.md_viewer.grid(row=0, 
                            column=2, 
                            sticky=N+S+E+W)  # Add these parameters

    def update_md_files(self):
        # Empty the list
        self.md_listbox.delete(0, 'end')

        # Get list of files in directory
        files = os.listdir(self.md_directory)
        md_files = [file for file in files if file.endswith('.md')]

        # Add files to listbox
        for file in md_files:
            self.md_listbox.insert('end', file)

    def on_md_file_select(self, evt):
        # Get selected file name
        idxs = self.md_listbox.curselection()
        if len(idxs)==1:
            idx = int(idxs[0])
            md_file = self.md_listbox.get(idx)
            
            # Read and convert the markdown file to HTML
            with open(os.path.join(self.md_directory, md_file), 'r') as f:
                md_text = f.read()
            html = markdown.markdown(md_text)
            
            # Display HTML in the viewer
            self.md_viewer.set_html(html)
    
    # TAB 3
    def create_history_sidebar(self, parent):
        self.history_listbox = Listbox(parent)
        self.history_listbox.grid(row=0, 
                            column=0, 
                            sticky=N+S+E+W)
        
        scrollbar = Scrollbar(parent, orient="vertical", command=self.history_listbox.yview)
        scrollbar.grid(row=0,
                          column=1,
                          sticky=N+S)
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        
        # Load the list of markdown files
        self.update_history_files()
        
        # Add event handler for selecting an item
        
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_file_select)
        
    def create_history_viewer(self, parent):
        self.history_viewer = HTMLLabel(parent, html="<h1>Select a file from the list</h1>")
        self.history_viewer.grid(row=0,
                                column=2,
                                sticky=N+S+E+W)
        
    def update_history_files(self):
        # Empty the list
        self.history_listbox.delete(0, 'end')
        
        # Get list of files in directory
        files = os.listdir(self.history_directory)
        history_files = [file for file in files if file.endswith('.md')]
        
        # Add files to listbox
        for file in history_files:
            self.history_listbox.insert('end', file)

    def on_history_file_select(self, evt):
        # Get selected file name
        idxs = self.history_listbox.curselection()
        if len(idxs)==1:
            idx = int(idxs[0])
            history_file = self.history_listbox.get(idx)
            
            # Read and convert the markdown file to HTML
            with open(os.path.join(self.history_directory, history_file), 'r') as f:
                history_text = f.read()
            html = markdown.markdown(history_text)
            
            # Display HTML in the viewer
            
            
            self.history_viewer.set_html(html)
    
    def create_img_sidebar(self, parent):
        self.img_listbox = Listbox(parent)
        self.img_listbox.grid(row=0, 
                              column=0, 
                              sticky=N+S+E+W)

        scrollbar = Scrollbar(parent, orient="vertical", command=self.img_listbox.yview)
        scrollbar.grid(row=0, 
                      column=1, 
                      sticky=N+S)  
        self.img_listbox.config(yscrollcommand=scrollbar.set)

        # Load the list of image files
        self.update_img_files()

        # Add event handler for selecting an item
        self.img_listbox.bind('<<ListboxSelect>>', self.on_img_file_select)

    def create_img_viewer(self, parent):
        self.img_canvas = Canvas(parent)
        self.img_canvas.grid(row=0,
                            column=2,
                            sticky=N + S + E + W)

        # bind canvas resize event to a method
        self.img_canvas.bind("<Configure>", self.resize_image)

    def update_img_files(self):
        # Empty the list
        self.img_listbox.delete(0, 'end')

        # Get list of files in directory
        files = os.listdir(self.img_directory)
        img_files = [file for file in files if file.endswith('.png') or file.endswith('.jpg')]

        # Add files to listbox
        for file in img_files:
            self.img_listbox.insert('end', file)

    def on_img_file_select(self, evt):
        # Get selected file name
        idxs = self.img_listbox.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            img_file = self.img_listbox.get(idx)

            # Open and display the image file
            img_path = os.path.join(self.img_directory, img_file)
            self.image = Image.open(img_path)
            self.photo = ImageTk.PhotoImage(self.image)
            self.img_canvas.create_image(0, 0, image=self.photo, anchor="nw")

            # Keep a reference to the image object
            self.img_canvas.image = self.photo

            # Call to make sure the image is resized appropriately
            self.resize_image(None)

    def resize_image(self, event):
        # Get new dimensions
        width = self.img_canvas.winfo_width()
        height = self.img_canvas.winfo_height()

        # Resize and display the image
        resized_image = self.image.resize((width, height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)
        self.img_canvas.create_image(0, 0, image=self.photo, anchor="nw")
    
    def add_to_chat_history(self):
        # Get the currently selected file
        selection = self.md_listbox.curselection()

        if selection:
            selected_file = self.md_listbox.get(selection[0])

            # Open and read the file
            with open(os.path.join(self.md_directory, selected_file), 'r') as file:
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

    def run(self):
        # logic to create and manage tkinter root, e.g., root = tk.Tk()
        # and then...
        self.root.mainloop()

if __name__ == "__main__":
    chatbot_gui = ChatbotGUI()
    chatbot_gui.run()