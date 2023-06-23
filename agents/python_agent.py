import io
from contextlib import redirect_stdout
from typing import List, Dict, Union

class PythonRepl:
    def __init__(
            self, 
            model: str = "gpt-4-0613", 
            temperature: float = 0.2, 
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
        # Python REPL Agent
        You have access to a Python Interpreter through your python_repl function.
        Make sure the code you execute does not contain any malicious commands!
        Think steps ahead and make sure the code you execute correctly handles the users request.
        If anything is unclear, ask the user for clarification.
        When you are certain that the code is safe to execute, use the python_repl function to execute it.
        """

    def python_repl(self, code: str) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            try:
                exec(code, {"__name__": "__main__"})
            except Exception as e:
                return f"An error occurred while running the code: {str(e)}"
        return buffer.getvalue()

    @property
    def python_repl_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
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
