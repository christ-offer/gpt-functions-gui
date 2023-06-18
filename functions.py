import io
import os
import requests
from contextlib import redirect_stdout
from bs4 import BeautifulSoup
import markdown
import pandas as pd
import torch
import open_clip
from PIL import Image
import tempfile
import urllib

from utils import is_valid_filename, ensure_directory_exists

# Define the directory where the knowledgebase files are stored
KB_DIR = "./kb"

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

def wolfram_language_query(query: str) -> str:
    url = "http://api.wolframalpha.com/v1/result"
    params = {"appid": os.environ.get("WOLFRAM_APP_ID"), "i": query}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        return response.text
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
        return content  # Return content directly without conversion to HTML
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

function_params = [
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
    },
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
    },
    #{
    #    "name": "wolfram_language_query",
    #    "description": "Executes a Wolfram Language query and returns the result as a JSON string.",
    #    "parameters": {
    #        "type": "object",
    #        "properties": {
    #            "query": {"type": "string", "description": "The Wolfram Language query to execute. Must be a SINGLE LINE STRING!"},
    #        },
    #        "required": ["query"],
    #    },
    #},
]