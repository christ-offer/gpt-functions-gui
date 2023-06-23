import requests
from typing import Dict, List, Union

class WikidataAgent:
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
        # Wikidata SPARQL Query Agent
        This agent executes a SPARQL query on Wikidata and returns the result as a JSON string.
        Always think step by step to be certain that you have the correct query.
        If anything is unclear, please ask the user for clarification.
        """

    def wikidata_sparql_query(self, query: str) -> str:
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
            return f"An error occurred: {str(e)}"

    @property
    def wikidata_sparql_query_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
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
