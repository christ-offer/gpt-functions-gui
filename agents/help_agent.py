from typing import Dict, List, Union

class HelpAgent:
    def __init__(
            self, 
            model: str = "gpt-4-0613", 
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
        # Help Agent
        You call the help function and return the list of available commands.
        """

    def help(self) -> str:
        return """
        ### Available commands:
        * /help
        * /csv - csv handler
        * /python - python interpreter
        * /kb - knowledge base handler
        * /history - history handler
        * /write - file writer
        * /read - file reader
        * /edit - file editor
        * /wikidata - wikidata sparql handler
        * /image - image to text captioner
        * /scrape - web scraper
        """

    @property
    def help_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "help",
                "description": "Displays help message",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]
