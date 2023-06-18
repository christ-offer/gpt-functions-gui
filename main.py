import os
import markdown
import re
import openai
import json
import sys
import requests
import io
import html2text
import logging
import pandas as pd
from contextlib import redirect_stdout
from typing import Optional, Dict, List, Tuple


# Define the directory where the knowledgebase files are stored
KB_DIR = "./kb"

# Regular expression for a valid filename
VALID_FILENAME_RE = r'^[\w,\s-]+\.[A-Za-z]{2,}$'

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def is_valid_filename(filename: str) -> bool:
    return re.match(VALID_FILENAME_RE, filename) is not None

def ensure_directory_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)

def wikidata_sparql_query(query: str) -> str:
    url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "SPARQL Query GPT"
    }
    params = {"query": query, "format": "json"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        json_response = response.json()

        head = json_response.get("head", {}).get("vars", [])
        results = json_response.get("results", {}).get("bindings", [])

        # Convert the 'head' and 'results' into strings and return them
        result_str = 'Variables: ' + ', '.join(head) + '\n'
        result_str += 'Results:\n'
        for result in results:
            for var in head:
                result_str += f'{var}: {result.get(var, {}).get("value", "N/A")}\n'
            result_str += '\n'
        return result_str
    except requests.HTTPError as e:
        return f"A HTTP error occurred: {str(e)}"
    except requests.RequestException as e:
        return f"A request exception occurred: {str(e)}"
    except Exception as e:
        return f"An error occurred: {e}"

# Scrape a webpage and return the text content
def scrape_webpage(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        # Extract the text from the webpage
        html = response.text
        text = html2text.html2text(html)

        return text
    except requests.HTTPError as e:
        return f"A HTTP error occurred: {str(e)}"
    except requests.RequestException as e:
        return f"A request exception occurred: {str(e)}"
    except Exception as e:
        return f"An error occurred: {e}"

def write_code_file(filename: str, content: str) -> str:
    if not is_valid_filename(filename):
        return f"Invalid filename: {filename}"
    # directory = os.path.dirname(filename)
    # ensure_directory_exists(directory)
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"File '{filename}' has been successfully written."
    except Exception as e:
        return f"An error occurred while writing the file: {str(e)}"

def knowledgebase_create_entry(filename: str, content: str) -> str:
    if not is_valid_filename(filename):
        return "The provided filename is not valid."
    
    ensure_directory_exists(KB_DIR)
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
    ensure_directory_exists(KB_DIR)
    try:
        entries = os.listdir(KB_DIR)
        entries_str = '\n'.join(entries)
        return f"The knowledgebase contains the following entries:\n{entries_str}"
    except Exception as e:
        return f"An error occurred while listing the entries: {str(e)}"

def python_repl(code: str) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        try:
            exec(code, {"__name__": "__main__"})
        except Exception as e:
            return f"An error occurred while running the code: {str(e)}"
    return buffer.getvalue()

def read_csv_columns(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
        return ', '.join(columns) # Return the list as a string
    except FileNotFoundError:
        return f"The file '{file_path}' does not exist."
    except Exception as e:
        return f"An error occurred while reading the CSV file: {str(e)}"


def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({"role": "system", "content": "Personal Assistant AI, solves all problems like an 150 IQ expert in any field. Only use functions when necessary."})
    conversation.append({"role": "user", "content": prompt})
    # Replace this with your actual OpenAI secret key
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=conversation,
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
            {
                "name": "read_csv_columns",
                "description": "Reads column names from a CSV file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "The path of the CSV file to read."},
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "write_code_file",
                "description": "Writes a file to the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename for the new entry."},
                        "content": {"type": "string", "description": "The content for the new entry."},
                    },
                    "required": ["filename", "content"],
                },
            },
            {
                "name": "wikidata_sparql_query",
                "description": "Executes a SPARQL query on Wikidata and returns the result as a JSON string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The SPARQL query to execute. Must be a SINGLE LINE STRING!"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_webpage",
                "description": "Scrapes a webpage and returns the result as a JSON string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL of the webpage to scrape."},
                    },
                    "required": ["url"],
                },
            }
        ],
        function_call="auto",
    )


    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        logging.info(f"Function name: {function_name}")
        logging.info(f"Function arguments: {function_args}")

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

        logging.info(f"Function response: {function_response}")
        
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
if __name__ == "__main__":
    main()