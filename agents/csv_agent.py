import pandas as pd
from typing import List, Dict, Union

class CSVHandler:
    def __init__(
            self, 
            model: str = "gpt-3.5-turbo-16k-0613", 
            temperature: float = 0.0, 
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
        # CSV Agent
        You are responsible for handling CSV files.
        """
        
    def read_csv_columns(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path, nrows=0)
            columns = df.columns.tolist()

            # Prepare the markdown unordered list format
            markdown_list = '\n'.join([f'- {column}' for column in columns])

            return f"Here are the columns from '{file_path}':\n\n{markdown_list}"

        except FileNotFoundError:
            return f"The file '{file_path}' does not exist."

        except Exception as e:
            return f"An error occurred while reading the CSV file: {str(e)}"

    @property
    def read_csv_columns_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
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
