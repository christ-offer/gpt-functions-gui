import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Union


class Scraper:
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
        # Scrape Webpage Agent
        This agent scrapes a webpage and returns the result as a JSON string.
        """

    def scrape_webpage(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

            # Parse the webpage with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Define the tags to be removed
            tags = ['a', 'img', 'script', 'style', 'svg', 'iframe', 'canvas', 'video', 'audio', 'map', 'noscript']

            # Remove each defined tag
            for tag in tags:
                for item in soup.find_all(tag):
                    item.decompose()

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
            return f"An error occurred: {str(e)}"

    @property
    def scrape_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
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
