import openai
import json
import logging
from typing import Optional, Dict, List, Tuple
import tkinter as tk
from tkinter import scrolledtext
from ttkthemes import ThemedTk
from tkinter import ttk
import tkinter.font as tkfont
import os
from tkinter import filedialog
import shutil

from functions import function_params, wikidata_sparql_query, scrape_webpage, write_code_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns, image_to_text

conversation = []

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

system_message = """PersonalAssistant {
  Constraints {
    You are incredibly intelligent and knowledgable
    You think step by step to make sure you have the right solution
    Before submitting SPARQL queries, make sure you fully understand the question
    You only use your functions when they are called
  }
  
  /python [idea] - Uses the python_repl function.
  /wikidata [question] - Uses the wikidata_sparql_query function
  /scrape [url] - Uses the scrape_webpage function
  /write_code [idea] - Generates code for the idea, uses the write_code_file function
  /kb_create [content] - Uses the knowledgebase_create_entry function
  /kb_list - Uses the knowledgebase_list_entries function
  /kb_read [entry_name] - Uses the knowledgebase_read_entry function
  /csv [filename] - Uses the read_csv_columns function
  /image_to_text [image] - Uses the image_to_text function
  /help - Returns a list of all available functions
}
"""

system_message2 = """
You recive the responses from the functions PersonalAssistant has called

STRICT Response format:
If the request fails, return an error message

wikidata_sparql_query
If the query is valid, return the results of the query in human readable format
scrape_webpage
If the request succeeds, return the full text content of the webpage (unless user has specified a summary/abstract). Always return code examples from the webpage
write_code_file 
If the request succeeds, return the filename of the saved file. Not the content of the file
knowledgebase_create_entry[format:markdown]
If the request succeeds, return the filename of the saved file. Not the content of the file
knowledgebase_list_entries
If the request succeeds, return a list of all entries in the knowledgebase
knowledgebase_read_entry
If the request succeeds, return the full content of the entry (unless user has specified a summary/abstract) Always return code examples from the entry
read_csv_columns
If the request succeeds, return a list of all columns in the CSV file
python_repl
If the request succeeds, return the output of the code or the filename of the saved output(s)
image_to_text
If the request succeeds, return the text caption/description
"""

def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({"role": "system", "content": system_message})
    conversation.append({"role": "user", "content": prompt})
    # Replace this with your actual OpenAI secret key
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=conversation,
        functions=function_params,
        function_call="auto",
    )

    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        print(f"Function name: {function_name}")
        print(f"Function arguments: {function_args}")

        if function_name == "python_repl":
            function_response = python_repl(function_args.get("code"))
        elif function_name == "knowledgebase_read_entry":
            function_response = knowledgebase_read_entry(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name in ["knowledgebase_create_entry","knowledgebase_update_entry", "knowledgebase_list_entries", "read_csv_columns", "write_code_file"]:
            function_response = globals()[function_name](*function_args.values())
        elif function_name == "wikidata_sparql_query":
            function_response = wikidata_sparql_query(function_args.get("query"))
        elif function_name == "scrape_webpage":
            function_response = scrape_webpage(function_args.get("url"))
        elif function_name == "image_to_text":
            function_response = image_to_text(function_args.get("filename"))

        logging.info(f"Function response: {function_response}")
        
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": system_message2},
                {"role": "user", "content": prompt},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        conversation.append(second_response["choices"][0]["message"]) 
        return second_response["choices"][0]["message"]["content"], conversation  # Return the conversation here
    else:
        conversation.append(message)
        return message["content"], conversation

# CLI
#def main():
#    print("Welcome to the CLI-chatbot. Type 'exit' to quit.")
#    conversation = []
#    while True:
#        user_input = input("You: ")
#        if user_input.lower() == "exit":
#            print("Goodbye!")
#            break

#        try:
#            response, conversation = run_conversation(user_input, conversation)
#            print(f"Bot: {response}")
#        except Exception as e:
#            print(f"An error occurred: {e}")
#if __name__ == "__main__":
#    main()

# GUI
class ChatbotGUI:
    def __init__(self):
        self.root = ThemedTk(theme="arc") # Choose a suitable theme
        self.root.title('Chatbot')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)  # Give sidebar and main frame different weight
        self.root.grid_columnconfigure(1, weight=4)
        self.conversation = []  # Add this line
        self.create_widgets()

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
        
        # Add a theme dropdown
        available_themes = self.root.get_themes()  # get the list of themes
        self.theme_var = tk.StringVar()  # create a StringVar to hold selected theme
        self.theme_var.set(self.root.set_theme)  # set initial value to the current theme
        theme_dropdown = ttk.Combobox(self.sidebar, textvariable=self.theme_var, values=available_themes)
        theme_dropdown.pack()
        theme_dropdown.bind('<<ComboboxSelected>>', self.change_theme)  # bind the selection event to the change_theme method



        # Add a reset button
        reset_button = ttk.Button(self.sidebar, text='Reset Conversation', command=self.reset_conversation)
        reset_button.pack()
        
        # Add an image upload button
        upload_button = ttk.Button(self.sidebar, text='Upload Image', command=self.upload_image)
        upload_button.pack()
        
        # Add a csv upload button
        upload_csv_button = ttk.Button(self.sidebar, text='Upload CSV', command=self.upload_csv)
        upload_csv_button.pack()
        
    def upload_image(self):
        image_file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if image_file_path:
            target_directory = "data/images"
            os.makedirs(target_directory, exist_ok=True)
            target_file_path = os.path.join(target_directory, os.path.basename(image_file_path))
            import shutil
            shutil.copy(image_file_path, target_file_path)
            
            caption = image_to_text(image_file_path)
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
        self.text_area = scrolledtext.ScrolledText(frame, wrap='word', font=('Ubuntu', 20))
        self.text_area.tag_configure("user", background="lightgray", spacing3=10)  # style for user text
        self.text_area.tag_configure("bot", background="lightblue", spacing3=10)  # style for bot text
        self.text_area.grid(row=0, column=0, sticky='nsew')

    def create_input_area(self, frame):
        bottom_frame = ttk.Frame(frame)
        bottom_frame.grid(sticky='nsew')

        self.user_input_text = scrolledtext.ScrolledText(bottom_frame, wrap='word', height=1, font=('Ubuntu', 20)) # Set the font size and height
        self.user_input_text.grid(row=0, column=0, sticky='nsew')

        send_button = ttk.Button(bottom_frame, text='Send', command=self.run_chat)
        send_button.grid(row=0, column=1)

        bottom_frame.grid_columnconfigure(0, weight=1)
    
    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.root.set_theme(selected_theme)
    
    def run_chat(self, event=None):
        user_input = self.user_input_text.get("1.0", tk.END).strip()
        try:
            response, _ = run_conversation(user_input, self.conversation)
        except Exception as e:
            response = f"Error: {str(e)}"
        self.text_area.insert(tk.INSERT, f'You: {user_input}\n', "user")
        self.text_area.insert(tk.INSERT, f'Bot: {response}\n', "bot")
        self.user_input_text.delete("1.0", tk.END)


    def reset_conversation(self):
        self.conversation = []
        self.text_area.delete('1.0', tk.END)

    def run(self):
        self.root.mainloop()



if __name__ == "__main__":
    chatbot_gui = ChatbotGUI()
    chatbot_gui.run()