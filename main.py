import os
import markdown
import re
import openai
import json
from typing import Optional, Dict
import requests
import sys
import io
from contextlib import redirect_stdout

# Define the directory where the knowledgebase files are stored
KB_DIR = "./kb"

# Regular expression for a valid filename
VALID_FILENAME_RE = r'^[\w,\s-]+\.[A-Za-z]{2,}$'

def is_valid_filename(filename: str) -> bool:
    return re.match(VALID_FILENAME_RE, filename) is not None

def knowledgebase_create_entry(filename: str, content: str) -> str:
    if not is_valid_filename(filename):
        return "The provided filename is not valid."
    
    filepath = os.path.join(KB_DIR, filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Entry '{filename}' has been successfully created."
    except Exception as e:
        return f"An error occurred while creating the entry: {str(e)}"

def knowledgebase_read_entry(filename: str) -> str:
    if not is_valid_filename(filename):
        return "The provided filename is not valid."
    
    filepath = os.path.join(KB_DIR, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        # Convert markdown content to HTML for better readability
        html_content = markdown.markdown(content)
        return html_content
    except Exception as e:
        return f"An error occurred while reading the entry: {str(e)}"

def knowledgebase_update_entry(filename: str, content: str) -> str:
    if not is_valid_filename(filename):
        return "The provided filename is not valid."
    
    filepath = os.path.join(KB_DIR, filename)
    
    if not os.path.exists(filepath):
        return "The specified entry does not exist."
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Entry '{filename}' has been successfully updated."
    except Exception as e:
        return f"An error occurred while updating the entry: {str(e)}"

def knowledgebase_list_entries() -> str:
    try:
        entries = os.listdir(KB_DIR)
        entries_str = '\n'.join(entries)
        return f"The knowledgebase contains the following entries:\n{entries_str}"
    except Exception as e:
        return f"An error occurred while listing the entries: {str(e)}"

def python_repl(code: str) -> str:
    # Create a buffer to hold the output
    buffer = io.StringIO()

    # Run the code, redirecting stdout to the buffer
    with redirect_stdout(buffer):
        try:
            exec(code, {"__name__": "__main__"})
        except Exception as e:
            return f"An error occurred while running the code: {e}"

    # Return the output
    return buffer.getvalue()

def run_conversation(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "user", "content": prompt}
            ],
        functions=[
            {
                "name": "python_repl",
                "description": "Executes the provided Python code and returns the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "The Python code to execute. Remember to print the output!"},
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "knowledgebase_create_entry",
                "description": "Creates a new knowledge base entry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename for the new entry."},
                        "content": {"type": "string", "description": "The content for the new entry. Format: Markdown."},
                    },
                    "required": ["filename", "content"],
                },
            },
            {
                "name": "knowledgebase_read_entry",
                "description": "Reads an existing knowledge base entry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename of the entry to read."},
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "knowledgebase_update_entry",
                "description": "Updates an existing knowledge base entry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename of the entry to update."},
                        "content": {"type": "string", "description": "The new content for the entry. Format: Markdown."},
                    },
                    "required": ["filename", "content"],
                },
            },
            {
                "name": "knowledgebase_list_entries",
                "description": "Lists all entries in the knowledge base",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ],
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
                               "knowledgebase_update_entry", "knowledgebase_list_entries"]:
            function_response = globals()[function_name](*function_args.values())

        print(f"Function response: {function_response}")
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": "The following is the response from the function call:"},
                {"role": "user", "content": prompt},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        return second_response["choices"][0]["message"]["content"]
    else:
        return message["content"]

def main():
    print("Welcome to the CLI-chatbot. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        try:
            response = run_conversation(user_input)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
