from typing import List, Dict, Union
import os
from utils import ensure_directory_exists, is_valid_filename

from constants import PROJECTS_DIR
from agents.file_write_agent import FileWriter



class ProjectWriter:
    def __init__(
            self, model: str = "gpt-4-0613", 
            temperature: float = 0.2, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        self.file_writer = FileWriter()
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.system_message = """# Code Writing Agent
You will recieve a Ticket and a Spec for a project.
Your job is to write the code for every file in the project using your write_files function.
Approach the task methodically to ensure clarity, accuracy, and thoroughness, just as an experienced senior software engineer would.
You ALWAYS use your write_files function to write files. That is your only job.
"""
    
    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def top_p(self):
        return self._top_p

    @top_p.setter
    def top_p(self, value):
        self._top_p = value

    @property
    def frequency_penalty(self):
        return self._frequency_penalty

    @frequency_penalty.setter
    def frequency_penalty(self, value):
        self._frequency_penalty = value

    @property
    def presence_penalty(self):
        return self._presence_penalty

    @presence_penalty.setter
    def presence_penalty(self, value):
        self._presence_penalty = value
    
    def write_files(self, files: List[Dict[str, str]]) -> str:
      try:
          for file in files:
              try:
                  filename = file['filename']
                  content = file['content']
              except KeyError as e:
                  raise ValueError(f"File dictionary missing key: {str(e)}")

              # Get the directory part of the filename
              sub_dirs, filename_only = os.path.split(filename)

              # Join the root directory with the subdirectories
              full_dir = os.path.join(PROJECTS_DIR, sub_dirs)

              # Create the directories if they don't exist
              os.makedirs(full_dir, exist_ok=True)

              self.file_writer.write_file(filename_only, content, directory=full_dir)
          
          return f"Files have been successfully written to {PROJECTS_DIR}."
      
      except Exception as e:
          print(f"An error occurred while writing files: {str(e)}")
          raise

    @property
    def write_files_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "write_files",
                "description": "Writes the files from the Ticket/Spec.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "description": "The files to write.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "filename": {
                                        "type": "string",
                                        "description": "The name of the file to write.",
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "The content of the file to write.",
                                    },
                                },
                                "required": ["filename", "content"],
                            },
                        },
                    },
                    "required": ["files"],
                },
            }
        ]