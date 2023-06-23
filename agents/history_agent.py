import os
from typing import List, Dict, Union
from agents.file_write_agent import FileWriter
from utils import ensure_directory_exists
from utils import is_valid_filename
from constants import HISTORY_DIR

file_writer = FileWriter()

class HistoryHandler:
    def __init__(
            self, model: str = "gpt-4-0613", 
            temperature: float = 0.3, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0,
            conversation = []
            ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.conversation = conversation,
        self.system_message = """
        # History Agent
        You are responsible for handling the history.
        """
        self.HISTORY_DIR = HISTORY_DIR

    def history_create_entry(self, filename: str, content) -> str:
        return file_writer.write_file(filename, content, directory=self.HISTORY_DIR)

    def history_list_entries(self) -> str:
        ensure_directory_exists(self.HISTORY_DIR)
        try:
            entries = os.listdir(self.HISTORY_DIR)
            entries_str = '\n'.join(entries)
            return f"The history contains the following entries:\n{entries_str}"
        except Exception as e:
            return f"An error occurred while listing the entries: {str(e)}"

    def history_read_entry(self, filename: str) -> str:
        if not is_valid_filename(filename):
            return "The provided filename is not valid."

        filepath = os.path.join(self.HISTORY_DIR, filename)

        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return content  # Return content directly without conversion to HTML
        except Exception as e:
            return f"An error occurred while reading the entry: {str(e)}"

    @property
    def history_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "history_create_entry",
                "description": "Creates a new history entry",
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
                "name": "history_read_entry",
                "description": "Reads an existing history entry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename of the entry to read."},
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "history_list_entries",
                "description": "Lists all entries in the history",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]
