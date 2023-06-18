import openai
import json
import gradio as gr
import logging
from typing import Optional, Dict, List, Tuple

from functions import function_params, wikidata_sparql_query, scrape_webpage, write_code_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns, image_to_text
import tkinter as tk
from tkinter import scrolledtext
from ttkthemes import ThemedTk
from tkinter import ttk
import tkinter.font as tkfont

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
        elif function_name in ["knowledgebase_create_entry", "knowledgebase_read_entry", 
                               "knowledgebase_update_entry", "knowledgebase_list_entries", 
                               "read_csv_columns", "write_code_file"]:
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

def main():
    print("Welcome to the CLI-chatbot. Type 'exit' to quit.")
    conversation = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        try:
            response, conversation = run_conversation(user_input, conversation)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"An error occurred: {e}")
#if __name__ == "__main__":
#    main()
    

# GUI
class ChatbotGUI:
    def __init__(self):
        self.root = ThemedTk(theme="arc") # Choose a suitable theme
        self.root.title('Chatbot')
        self.create_widgets()

    def create_widgets(self):
        self.create_text_area()
        self.create_input_area()
        self.root.bind('<Return>', self.run_chat)  # If you press 'Enter', it will trigger the run_chat function

    def create_text_area(self):
        frame = ttk.Frame(self.root)
        frame.grid(sticky='nsew')

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.text_area = scrolledtext.ScrolledText(frame, wrap='word', font=('Ubuntu', 20)) # Set the font size
        self.text_area.grid(row=0, column=0, sticky='nsew')

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def create_input_area(self):
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.grid(sticky='nsew')

        self.user_input_text = scrolledtext.ScrolledText(bottom_frame, wrap='word', height=1, font=('Ubuntu', 20)) # Set the font size and height
        self.user_input_text.grid(row=0, column=0, sticky='nsew')

        send_button = ttk.Button(bottom_frame, text='Send', command=self.run_chat)
        send_button.grid(row=0, column=1)

        bottom_frame.grid_columnconfigure(0, weight=1)

    def run_chat(self, event=None):
        """
        Process the user input and display the bot's response in the text area.
        """
        user_input = self.user_input_text.get("1.0", tk.END).strip()
        try:
            response, _ = run_conversation(user_input, conversation)
        except Exception as e:
            response = f"Error: {str(e)}"
        self.text_area.insert(tk.INSERT, f'You: {user_input}\n')
        self.text_area.insert(tk.INSERT, f'Bot: {response}\n')
        self.user_input_text.delete("1.0", tk.END)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    chatbot_gui = ChatbotGUI()
    chatbot_gui.run()