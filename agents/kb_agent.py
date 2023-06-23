import os
from typing import List, Dict, Union
from agents.file_write_agent import FileWriter
from utils import ensure_directory_exists
from utils import is_valid_filename
from constants import KB_DIR

file_writer = FileWriter()

class KnowledgebaseHandler:
    def __init__(
            self, model: str = "gpt-4-0613", 
            temperature: float = 0.3, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.system_message = """
        # Knowledgebase Agent
        You are responsible for handling the knowledgebase.
        """
        self.KB_DIR = KB_DIR

    def knowledgebase_create_entry(self, filename: str, content: str) -> str:
        return file_writer.write_file(filename, content, directory=self.KB_DIR)

    def knowledgebase_list_entries(self) -> str:
        ensure_directory_exists(self.KB_DIR)
        try:
            entries = os.listdir(self.KB_DIR)
            entries_str = '\n'.join(entries)
            return f"The knowledgebase contains the following entries:\n{entries_str}"
        except Exception as e:
            return f"An error occurred while listing the entries: {str(e)}"

    def knowledgebase_read_entry(self, filename: str) -> str:
        if not is_valid_filename(filename):
            return "The provided filename is not valid."

        filepath = os.path.join(self.KB_DIR, filename)

        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return content  # Return content directly without conversion to HTML
        except Exception as e:
            return f"An error occurred while reading the entry: {str(e)}"

    @property
    def knowledgebase_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
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