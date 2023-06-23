from agents.csv_agent import CSVHandler
from agents.python_agent import PythonRepl
from agents.kb_agent import KnowledgebaseHandler
from agents.history_agent import HistoryHandler
from agents.file_write_agent import FileWriter
from agents.scrape_agent import Scraper
from agents.wikidata_agent import WikidataAgent
from agents.image_agent import ImageAgent
from agents.help_agent import HelpAgent



class FunctionCallAgent:
    def __init__(self):
        self.csv_handler = CSVHandler()
        self.python_repl = PythonRepl()
        self.kb_handler = KnowledgebaseHandler()
        self.history_handler = HistoryHandler()
        self.file_handler = FileWriter()
        self.scraper = Scraper()
        self.wikidata_agent = WikidataAgent()
        self.image_agent = ImageAgent()
        self.help_agent = HelpAgent()
        self.functions_that_append_to_conversation = {
            "knowledgebase_read_entry", 
            "knowledgebase_list_entries", 
            "read_history_entry", 
            "list_history_entries", 
            "read_file",
            "read_csv_columns",
            "scrape_webpage",
            "help"
        }

        self.function_map = {
            "python_repl": self.python_repl.python_repl,
            "knowledgebase_read_entry": self.kb_handler.knowledgebase_read_entry,
            "knowledgebase_list_entries": self.kb_handler.knowledgebase_list_entries,
            "knowledgebase_create_entry": self.kb_handler.knowledgebase_create_entry,
            "read_history_entry": self.history_handler.history_read_entry,
            "write_history_entry": self.history_handler.history_create_entry,
            "list_history_entries": self.history_handler.history_list_entries,
            "read_csv_columns": self.csv_handler.read_csv_columns,
            "write_file": self.file_handler.write_file,
            "read_file": self.file_handler.read_file,
            "edit_file": self.file_handler.edit_file,
            "wikidata_sparql_query": self.wikidata_agent.wikidata_sparql_query,
            "scrape_webpage": self.scraper.scrape_webpage,
            "image_to_text": self.image_agent.image_to_text,
            "help": self.help_agent.help,
        }
        