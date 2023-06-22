import io
import os
from typing import List, Dict
import requests
from contextlib import redirect_stdout
from bs4 import BeautifulSoup
import markdown
import pandas as pd
import torch
import open_clip
from PIL import Image
import urllib

from utils import is_valid_filename, ensure_directory_exists

# Define the directories where files are stored
KB_DIR = "./kb"
HISTORY_DIR = "./history"
DATA_DIR = "./data"
IMAGE_DIR = "./data/images"
CSV_DIR = "./data/csv"
CODE_DIR = "./data/code"
SCRAPE_DIR = "./data/scrape"
PROJECTS_DIR = "data/code/projects/"

# WIKIDATA
# Define function, params and system message for Wikidata SPARQL Query Agent
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


wikidata_sparql_query_params = [
    {
        "name": "wikidata_sparql_query",
        "description": "Executes a SPARQL query on Wikidata and returns the result as a JSON string.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The SPARQL query to execute."},
            },
            "required": ["query"],
        },
    }
]

wikidata_system_message = """
# Wikidata SPARQL Query Agent
This agent executes a SPARQL query on Wikidata and returns the result as a JSON string.
Always think step by step to be certain that you have the correct query.
If anything is unclear, please ask the user for clarification.
"""

# SCRAPE
# Define function, params and system message for scraping a webpage
def scrape_webpage(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        # Parse the webpage with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove any existing <a> tags (hyperlinks)
        for a in soup.find_all('a', href=True):
            a.decompose()

        # Remove any existing <img> tags (images)
        for img in soup.find_all('img', src=True):
            img.decompose()
        
        # Remove any existing <script> tags (JavaScript)
        for script in soup.find_all('script'):
            script.decompose()
        
        # Remove any existing <style> tags (CSS)
        for style in soup.find_all('style'):
            style.decompose()
            
        # Remove any existing <svg> tags (SVG)
        for svg in soup.find_all('svg'):
            svg.decompose()
        
        # Remove any existing <iframe> tags (iFrames)
        for iframe in soup.find_all('iframe'):
            iframe.decompose()
        
        # Remove any existing <canvas> tags (Canvas)
        for canvas in soup.find_all('canvas'):
            canvas.decompose()
            
        # Remove any existing <video> tags (Video)
        for video in soup.find_all('video'):
            video.decompose()
            
        # Remove any existing <audio> tags (Audio)
        for audio in soup.find_all('audio'):
            audio.decompose()
            
        # Remove any existing <map> tags (Image maps)
        for map in soup.find_all('map'):
            map.decompose()
            
        # Remove any existing <noscript> tags (JavaScript)
        for noscript in soup.find_all('noscript'):
            noscript.decompose()
            
            
        # Extract text from the parsed HTML
        text = soup.get_text()

        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    except requests.HTTPError as e:
        return f"A HTTP error occurred: {str(e)}"
    except requests.RequestException as e:
        return f"A request exception occurred: {str(e)}"
    except Exception as e:
        return f"An error occurred: {e}"

scrape_webpage_params = [
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
]

scrape_system_message = """
# Scrape Webpage Agent
This agent scrapes a webpage and returns the result as a JSON string.
"""


# IMAGE TO TEXT
# Define function, params and system message for converting an image to text
def image_to_text(image_path_or_url, seq_len=20):
    device = torch.device("cpu")

    try:
        model, _, transform = open_clip.create_model_and_transforms(
            "coca_ViT-L-14",
            pretrained="mscoco_finetuned_laion2B-s13B-b90k"
        )
        model.to(device)

        # Check if the image_path_or_url is a URL or local path
        if urllib.parse.urlparse(image_path_or_url).scheme in ['http', 'https']:
            response = requests.get(image_path_or_url)
            _, ext = os.path.splitext(urllib.parse.urlparse(image_path_or_url).path)
            file_name = urllib.parse.urlparse(image_path_or_url).path.split('/')[-1]
            with open(f'data/{file_name}', 'wb') as f:
                f.write(response.content)
            image = Image.open(f'data/{file_name}').convert("RGB")
        else:
            image = Image.open(image_path_or_url).convert("RGB")

        im = transform(image).unsqueeze(0).to(device)

        with torch.no_grad(), torch.cuda.amp.autocast():
            generated = model.generate(im, seq_len=seq_len)

        return open_clip.decode(generated[0].detach()).split("<end_of_text>")[0].replace("<start_of_text>", "")

    except FileNotFoundError:
        return f"No file found at {image_path_or_url}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

image_to_text_params = [
    {
        "name": "image_to_text",
        "description": "Creates a caption / description of an image.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The filename of the image to describe."},
            },
            "required": ["filename"],
        },
    }
]

image_to_text_system_message = """
# Image to Text Agent
This agent creates a caption / description of an image.
"""


# WRITE FILE
# Define function, params and system message for writing a file to the system
def write_file(filename: str, content: str, directory: str = DATA_DIR) -> str:
    if not is_valid_filename(filename):
        return f"Invalid filename: {filename}"
    
    ensure_directory_exists(directory)    
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"File '{filename}' has been successfully written to {directory}."
    except Exception as e:
        return f"An error occurred while writing the file: {str(e)}"
    
write_file_params = [
    {
        "name": "write_file",
        "description": "Writes a file to the system",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The filename for the new entry."},
                "content": {"type": "string", "description": "The content for the new entry."},
            },
            "required": ["filename", "content"],
        },
    }
]    

write_file_system_message = """
# Write File Agent
This agent writes a file to the system.
"""

# WRITE CODE
# Define function, params and system message for writing a code file to the system
def write_code(filename: str, content: str) -> str:
    return write_file(filename, content, directory=CODE_DIR)

write_code_params = [
    {
        "name": "write_code",
        "description": "Writes a code file to the system",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The filename for the new entry."},
                "content": {"type": "string", "description": "The code content for the new entry."},
            },
            "required": ["filename", "content"],
        },
    }
]

# KNOWLEDGEBASE
# Define function, params and system message for handling the knowledgebase
def knowledgebase_create_entry(filename: str, content: str) -> str:
    return write_file(filename, content, directory=KB_DIR)

def knowledgebase_list_entries() -> str:
    ensure_directory_exists(KB_DIR)
    try:
        entries = os.listdir(KB_DIR)
        entries_str = '\n'.join(entries)
        return f"The knowledgebase contains the following entries:\n{entries_str}"
    except Exception as e:
        return f"An error occurred while listing the entries: {str(e)}"

def knowledgebase_read_entry(filename: str) -> str:
    if not is_valid_filename(filename):
        return "The provided filename is not valid."
    
    filepath = os.path.join(KB_DIR, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content  # Return content directly without conversion to HTML
    except Exception as e:
        return f"An error occurred while reading the entry: {str(e)}"
    
knowledgebase_params = [
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
        "name": "knowledgebase_list_entries",
        "description": "Lists all entries in the knowledge base",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]

knowledgebase_system_message = """
# Knowledgebase Agent
You are responsible for handling the knowledgebase.
"""


# HISTORY
# Define function, params and system message for handling the history
def write_history_entry(filename: str, content: str) -> str:
    return write_file(filename, content, directory=HISTORY_DIR)
    
def read_history_entry(filename: str) -> str:
    if not is_valid_filename(filename):
        return "The provided filename is not valid."
    
    filepath = os.path.join(HISTORY_DIR, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content  # Return content directly without conversion to HTML
    except Exception as e:
        return f"An error occurred while reading the entry: {str(e)}"    

def list_history_entries() -> str:
    ensure_directory_exists(HISTORY_DIR)
    try:
        entries = os.listdir(HISTORY_DIR)
        entries_str = '\n'.join(entries)
        return f"The history contains the following entries:\n{entries_str}"
    except Exception as e:
        return f"An error occurred while listing the entries: {str(e)}"
    
history_params = [
    {
        "name": "write_history_entry",
        "description": "Writes a new entry to the history knowledge base.",
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
        "name": "read_history_entry",
        "description": "Reads an existing entry from the history knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The filename of the entry to read."},
            },
            "required": ["filename"],
        },
    },
    {
        "name": "list_history_entries",
        "description": "Lists all entries in the history knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]

history_system_message = """
# History Agent
You are responsible for handling the history.
"""


# PYTHON REPL
# Define function, params and system message for running Python code in the REPL
def python_repl(code: str) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        try:
            exec(code, {"__name__": "__main__"})
        except Exception as e:
            return f"An error occurred while running the code: {str(e)}"
    return buffer.getvalue()

python_repl_params = [
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
    }
]

python_repl_system_message = """
# Python REPL Agent
You are responsible for handling the Python REPL.
Make sure the code you execute does not contain any malicious commands!
Think steps ahead and make sure the code you execute correctly handles the users request.
If anything is unclear, ask the user for clarification.
"""


# CSV
# Define function, params and system message for reading CSV files (Returns column names)
def read_csv_columns(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
        return ', '.join(columns) # Return the list as a string
    except FileNotFoundError:
        return f"The file '{file_path}' does not exist."
    except Exception as e:
        return f"An error occurred while reading the CSV file: {str(e)}"

read_csv_columns_params = [
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
    }
]


csv_system_message = """
# CSV Agent
You are responsible for handling CSV files.
"""


# READ FILE
# Define function, params and system message for reading files
def read_file(filename: str) -> str:
    content = None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = f"The file '{filename}' does not exist."
    except Exception as e:
        content = f"An error occurred while reading the file: {str(e)}"
    return content

read_file_params = [
    {
        "name": "read_file",
        "description": "Reads the contents of the provided file and returns it.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The path to the file to read."},
            },
            "required": ["filename"],
        },
    }
]

read_file_system_message = """
# Read File Agent
You are responsible for reading files.
"""

# EDIT FILE
# Define function, params and system message for editing files
def edit_file(filepath: str, changes: List[Dict]) -> None:
    print(f"Editing file '{filepath}'...")
    print(f"Changes: {changes}")
    try:
        # Read the file into a list of lines
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Apply the changes
        for change in changes:
            for line_num in change['range']:
                if line_num <= len(lines):  # Ensure the line number is valid
                    lines[line_num-1] = change['replacementcontent'] + '\n'
                else:
                    print(f"Line number {line_num} is out of range in file {filepath}.")
                    return(f"Line number {line_num} is out of range in file {filepath}.")
                    
        # Write the modified lines back to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print(f"File '{filepath}' has been successfully edited.")
        return(f"File '{filepath}' has been successfully edited.")
            
    except FileNotFoundError:
        print(f"The file '{filepath}' does not exist.")
        return(f"The file '{filepath}' does not exist.")
    except Exception as e:
        print(f"An error occurred while editing the file: {str(e)}")
        return(f"An error occurred while editing the file: {str(e)}")


edit_file_params = [
    {
        "name": "edit_file",
        "description": "Edits the provided file by replacing the specified lines with the provided content.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "The path to the file to edit."},
                "changes": {
                    "type": "array",
                    "description": "The changes to apply to the file.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "range": {
                                "type": "array",
                                "description": "The line numbers to replace.",
                                "items": {"type": "integer"},
                            },
                            "replacementcontent": {
                                "type": "string",
                                "description": "The content to replace the lines with.",
                            },
                        },
                        "required": ["range", "replacementcontent"],
                    },
                },
            },
            "required": ["filepath", "changes"],
        },
    }
]

edit_file_system_message = """
# Edit File Agent
You are responsible for editing files.
"""


# HELP
# Define function, params and system message for displaying help
def help() -> str:
    return """Available commands:
    /help
    /python
    /kb
    /history
    /csv
    /code
    /scrape
    /projects
    /images
    /data
    """

help_params = [
    {
        "name": "help",
        "description": "Displays this help message",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


help_system_message = """
# Personal Assistant
You are an incredibly intelligent personal assistant.
You are responsible for handling the user's requests.
You always think step by step and make sure you understand the user's request to arrive at the correct and factual answer.
If anything is unclear, ask the user for clarification.

===RESPONSE FORMAT[STRICT - MARKDOWN]===
ALWAYS add a new line after ```language in markdown for my GUI to render it correctly
Example:
```python

print('Hello World')

```

Brainstorm:
- Problem;
- Approach;
- Technology;

Ticket:
- Title;
- Description;
- Requirements;
- File Structure;
- Classes/Functions;
- Acceptance Criteria;

Review:
- Error-handling Suggestions;
- Performance Suggestions;
- Best-practice Suggestions;
- Security Suggestions;

===FUNCTIONS[STRICT - ONLY WHEN SPECIFICALLY CALLED]===
/help - Displays a list of available commands.

===COMMANDS[STRICT - ONLY WHEN SPECIFICALLY CALLED]===
- brainstorm [n, topic] - Returns a list of n ideas for the topic following the response format.
- ticket [solution] - Returns a ticket for the solution following the response format.
- review [code|ticket] - Returns a review of the code|ticket following the response format.
"""






