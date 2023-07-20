import os
from tkinter import *
from tkinter import ttk

from agents.image_agent import ImageAgent
from agents.csv_agent import CSVHandler
from agents.file_write_agent import FileWriter
from agents.help_agent import HelpAgent
from agents.history_agent import HistoryHandler
from agents.kb_agent import KnowledgebaseHandler
from agents.scrape_agent import Scraper
from agents.python_agent import PythonRepl
from agents.wikidata_agent import WikidataAgent
from agents.write_project import ProjectWriter

class SettingsTab:
    def __init__(self, settings):
        self.image_agent = ImageAgent()
        self.csv_agent = CSVHandler()
        self.file_write_agent = FileWriter()
        self.help_agent = HelpAgent()
        self.history_agent = HistoryHandler()
        self.kb_agent = KnowledgebaseHandler()
        self.scrape_agent = Scraper()
        self.wikidata_agent = WikidataAgent()
        self.python_agent = PythonRepl()
        self.write_project = ProjectWriter()
        self.settings = settings  # add this line
        self.create_widgets_settings()

    def create_widgets_settings(self):
        self.settings.grid_rowconfigure(0, weight=1)
        self.settings.grid_columnconfigure(0, weight=0)
        self.settings.grid_columnconfigure(1, weight=5)

        self.create_settings_sidebar()
        self.create_settings_main()

    def create_settings_sidebar(self):
        self.sidebar_settings = ttk.Frame(self.settings, width=200)
        self.sidebar_settings.grid(row=0, column=0, sticky='nsew')
        self.sidebar_settings.grid_columnconfigure(0, weight=1)

        sidebar_label = ttk.Label(self.sidebar_settings, text="Settings")
        sidebar_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        agents_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../agents")  # Directory of agents
        agents = [f[:-3] for f in os.listdir(agents_dir) if f.endswith('.py') and f not in ["__init__.py", "function_mapper.py", "function_call_agent.py", "base_agent.py", "function_response_agent.py", "file_write_agent.py"]]

        self.agent_select = ttk.Combobox(self.sidebar_settings, values=agents)
        self.agent_select.set('Select Agent')  # Default text
        self.agent_select.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.agent_select.bind("<<ComboboxSelected>>", self.on_agent_selected)  # Bind the on_agent_selected function to the combobox

    def create_settings_main(self):
        config_frame = ttk.Frame(self.settings)  # pass self.settings as the parent widget
        config_frame.grid(row=0, column=1, sticky='nsew')
        
        # Create StringVar objects for the sliders
        self.temperature_var = StringVar(value=self.csv_agent.temperature)
        self.top_p_var = StringVar(value=self.csv_agent.top_p)
        self.frequency_penalty_var = StringVar(value=self.csv_agent.frequency_penalty)
        self.presence_penalty_var = StringVar(value=self.csv_agent.presence_penalty)
        self.system_message_var = StringVar(value=self.csv_agent.system_message)

        # For Model
        ttk.Label(config_frame, text="Model", anchor='e').grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.model_entry = ttk.Entry(config_frame)
        self.model_entry.insert(0, self.csv_agent.model)  # Set from CSVHandler
        self.model_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        
        # For Temperature
        ttk.Label(config_frame, text="Temperature", anchor='e').grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.temperature_label = ttk.Label(config_frame, textvariable=self.temperature_var) # Create a label with textvariable
        self.temperature_label.grid(row=1, column=1, padx=5, pady=5, sticky='n')
        self.temperature_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.temperature_var)
        self.temperature_scale.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # For Top_p
        ttk.Label(config_frame, text="Top_p", anchor='e').grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        self.top_p_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.top_p_var)
        self.top_p_label = ttk.Label(config_frame, textvariable=self.top_p_var)
        self.top_p_label.grid(row=3, column=1, padx=5, pady=5, sticky='n')
        self.top_p_scale.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # For Frequency Penalty
        ttk.Label(config_frame, text="Frequency Penalty", anchor='e').grid(row=5, column=0, padx=5, pady=5, sticky='ew')
        self.frequency_penalty_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.frequency_penalty_var)
        self.frequency_penalty_label = ttk.Label(config_frame, textvariable=self.frequency_penalty_var)
        self.frequency_penalty_label.grid(row=5, column=1, padx=5, pady=5, sticky='n')
        self.frequency_penalty_scale.grid(row=6, column=1, padx=5, pady=5, sticky='ew')


        # For Presence Penalty
        ttk.Label(config_frame, text="Presence Penalty", anchor='e').grid(row=7, column=0, padx=5, pady=5, sticky='ew')
        self.presence_penalty_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.presence_penalty_var)
        self.presence_penalty_label = ttk.Label(config_frame, textvariable=self.presence_penalty_var)
        self.presence_penalty_label.grid(row=7, column=1, padx=5, pady=5, sticky='n')
        self.presence_penalty_scale.grid(row=8, column=1, padx=5, pady=5, sticky='ew')
        
        # TODO Implement system messages text box
        ttk.Label(config_frame, text="System Message", anchor='e').grid(row=10, column=0, padx=5, pady=5, sticky='ew')
        self.system_message_text = Text(config_frame, width=60, height=40, wrap='word')
        self.system_message_text.grid(row=11, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        self.system_message_text.insert('1.0', self.csv_agent.system_message)
        

        apply_button = ttk.Button(config_frame, text='Apply', command=self.update_agent_settings)
        apply_button.grid(row=9, column=1, padx=5, pady=5, sticky='ew')
        pass

    def on_agent_selected(self, event):
        selected_agent = self.agent_select.get()
        self.agent = getattr(self, selected_agent)
        # Update the settings
        self.update_settings_from_agent()

    def update_settings_from_agent(self):
        self.model_entry.delete(0, 'end')
        self.model_entry.insert(0, self.agent.model)
        self.temperature_var.set(self.agent.temperature)
        self.top_p_var.set(self.agent.top_p)
        self.frequency_penalty_var.set(self.agent.frequency_penalty)
        self.presence_penalty_var.set(self.agent.presence_penalty)
        self.system_message_text.delete('1.0', 'end')
        self.system_message_text.insert('1.0', self.agent.system_message)
        pass

    def update_agent_settings(self):
        self.agent.model = self.model_entry.get() or "gpt-4-0613"
        self.agent.temperature = float(self.temperature_var.get() or 0.3)
        self.agent.top_p = float(self.top_p_var.get() or 1.0)
        self.agent.frequency_penalty = float(self.frequency_penalty_var.get() or 0.0)
        self.agent.presence_penalty = float(self.presence_penalty_var.get() or 0.0)
        self.agent.system_message = self.system_message_text.get('1.0', 'end-1c')
        pass
