    ## WIP: Work in progress - Pinecone integration and settings tab


    #def fetch_indexes(self):
    #    active_indexes = pinecone.list_indexes()
    #    return active_indexes
    #
    #def fetch_collections(self):
    #    active_collections = pinecone.list_collections()
    #    return active_collections
    
    #def create_widgets_tab3(self):
    #    self.tab3.grid_rowconfigure(0, weight=1)
    #    self.tab3.grid_columnconfigure(0, weight=1)
    #    self.tab3.grid_columnconfigure(1, weight=0)
    #    self.tab3.grid_columnconfigure(2, weight=4)
    #    ttk.Label(self.tab3, text="Pinecone").grid(column=0, row=0, padx=30, pady=30, sticky='nsew')
    #    self.create_sidebar_tab3(self.tab3)
    #    self.create_main_area3(self.tab3)

    #def create_sidebar_tab3(self, parent):
    #    self.sidebar_tab3 = ttk.Frame(parent, width=200)
    #    self.sidebar_tab3.grid(row=0, column=0, sticky='nsew')

    #    sidebar_label = ttk.Label(self.sidebar_tab3, text="Indexes")
    #    sidebar_label.pack()
        
    #    indexes = self.fetch_indexes()
    #    self.index_list = tk.Listbox(self.sidebar_tab3)
    #    for index in indexes:
    #        self.index_list.insert(tk.END, index)
    #    self.index_list.pack()
        
    #    sidebar_label = ttk.Label(self.sidebar_tab3, text="Collections")
    #    sidebar_label.pack()
        
    #    collections = self.fetch_collections()
    #    self.collection_list = tk.Listbox(self.sidebar_tab3)
    #    for collection in collections:
    #        self.collection_list.insert(tk.END, collection)
    #    self.collection_list.pack()
        
        
    #def create_main_area3(self, parent):
    #    main_frame = ttk.Frame(parent)
    #    main_frame.grid(row=0, column=2, sticky='nsew')
    #    main_frame.grid_rowconfigure(0, weight=1)
    #    main_frame.grid_columnconfigure(0, weight=1)

    #    self.create_text_area_tab3(main_frame)
    #    self.create_input_area_tab3(main_frame)

    #def create_text_area_tab3(self, frame):
    #    self.text_area_tab3 = tk.Text(frame, wrap='word', background="oldlace", height=10, font=('Ubuntu', 16)) 
    #    self.text_area_tab3.grid(row=0, column=0, sticky='nsew')

    #def create_input_area_tab3(self, frame):
    #    bottom_frame = ttk.Frame(frame)
    #    bottom_frame.grid(sticky='nsew')

    #    self.user_input_text_tab3 = tk.Entry(bottom_frame, background="oldlace", font=('Ubuntu', 16)) 
    #    self.user_input_text_tab3.grid(row=0, column=0, sticky='nsew')

    #    search_button = ttk.Button(bottom_frame, text='Search', command=self.run_search, style='TButton')
    #    search_button.grid(row=0, column=1)

    #    bottom_frame.grid_columnconfigure(0, weight=1)

    #def run_search(self):
        # Get the input query
    #    query_string = self.user_input_text_tab3.get()

        # Assuming you have a function `get_query_vector` that transforms the query into a vector
    #    query_vector = self.get_query_vector(query_string)

        # Initialize the index with the selected index from the Listbox
    #    selected_index = self.index_list.get(tk.ACTIVE)
    #    index = pinecone.Index(selected_index)

        # Run the query
    #    query_response = index.query(
    #        namespace='example-namespace',
    #        top_k=10,
    #        include_values=True,
    #        include_metadata=True,
    #        vector=query_vector,
            #filter={
            #    'genre': {'$in': ['comedy', 'documentary', 'drama']}
            #}
    #    )

        # Clear the text area
    #    self.text_area_tab3.delete('1.0', tk.END)

        # Insert the results into the text area
    #    for result in query_response.results:
    #        self.text_area_tab3.insert(tk.END, f'{result.id}: {result.score}\n')


    # def create_widgets_tab4(self):
    #     self.tab3.grid_rowconfigure(0, weight=1)
    #     self.tab3.grid_columnconfigure(0, weight=1)
    #     self.tab3.grid_columnconfigure(1, weight=0)
    #     self.tab3.grid_columnconfigure(2, weight=4)
        
    #     ttk.Label(self.tab4, text="Agent Configuration", justify=CENTER).grid(column=0, row=0, padx=30, pady=30, sticky='nsew')
    #     self.create_config_area(self.tab4)
    #     self.create_sidebar_tab4(self.tab4)
    
    # def create_sidebar_tab4(self, parent):
    #     self.sidebar_tab3 = ttk.Frame(parent, width=200)
    #     self.sidebar_tab3.grid(row=0, column=0, sticky='nsew')

    #     sidebar_label = ttk.Label(self.sidebar_tab3, text="Settings")
    #     sidebar_label.pack()

    #     # Create a combobox for the available agents
    #     agents = ['Agent1', 'Agent2', 'Agent3']  # Demo list of agents
    #     self.agent_select = ttk.Combobox(self.sidebar_tab3, values=agents)
    #     self.agent_select.set('Select Agent')  # Default text
    #     self.agent_select.pack(pady=10)  # Add some padding around the combobox

    # def update_temperature(self, value):
    #     rounded_value = round(float(value) * 10) / 10
    #     self.temperature_scale.set(rounded_value)
    #     self.temperature_var.set(str(rounded_value))

    # def update_top_p(self, value):
    #     rounded_value = round(float(value) * 10) / 10
    #     self.top_p_scale.set(rounded_value)
    #     self.top_p_var.set(str(rounded_value))

    # def update_frequency_penalty(self, value):
    #     rounded_value = round(float(value) * 10) / 10
    #     self.frequency_penalty_scale.set(rounded_value)
    #     self.frequency_penalty_var.set(str(rounded_value))

    # def update_presence_penalty(self, value):
    #     rounded_value = round(float(value) * 10) / 10
    #     self.presence_penalty_scale.set(rounded_value)
    #     self.presence_penalty_var.set(str(rounded_value))
    
    # def create_config_area(self, parent):
    #     config_frame = ttk.Frame(parent)
    #     config_frame.grid(row=1, column=0, sticky='nsew')

    #     # Create StringVar objects for the sliders
    #     self.temperature_var = StringVar()
    #     self.top_p_var = StringVar()
    #     self.frequency_penalty_var = StringVar()
    #     self.presence_penalty_var = StringVar()

    #     # For Model
    #     ttk.Label(config_frame, text="Model", anchor='e').grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    #     self.model_entry = ttk.Entry(config_frame)
    #     self.model_entry.insert(0, 'gpt-4-0613')  # Default value
    #     self.model_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    #     # For Temperature
    #     ttk.Label(config_frame, text="Temperature", anchor='e').grid(row=1, column=0, padx=5, pady=5, sticky='ew')
    #     self.temperature_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.temperature_var)
    #     self.temperature_scale.set(0.3)  # Default value
    #     self.temperature_label = ttk.Label(config_frame, textvariable=self.temperature_var)
    #     self.temperature_label.grid(row=1, column=1, padx=5, pady=5, sticky='n')
    #     self.temperature_scale.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
    #     # For Top_p
    #     ttk.Label(config_frame, text="Top_p", anchor='e').grid(row=3, column=0, padx=5, pady=5, sticky='ew')
    #     self.top_p_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.top_p_var)
    #     self.top_p_scale.set(1.0)  # Default value
    #     self.top_p_label = ttk.Label(config_frame, textvariable=self.top_p_var)
    #     self.top_p_label.grid(row=3, column=1, padx=5, pady=5, sticky='n')
    #     self.top_p_scale.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

    #     # For Frequency Penalty
    #     ttk.Label(config_frame, text="Frequency Penalty", anchor='e').grid(row=5, column=0, padx=5, pady=5, sticky='ew')
    #     self.frequency_penalty_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.frequency_penalty_var)
    #     self.frequency_penalty_scale.set(0.0)  # Default value
    #     self.frequency_penalty_label = ttk.Label(config_frame, textvariable=self.frequency_penalty_var)
    #     self.frequency_penalty_label.grid(row=5, column=1, padx=5, pady=5, sticky='n')
    #     self.frequency_penalty_scale.grid(row=6, column=1, padx=5, pady=5, sticky='ew')


    #     # For Presence Penalty
    #     ttk.Label(config_frame, text="Presence Penalty", anchor='e').grid(row=7, column=0, padx=5, pady=5, sticky='ew')
    #     self.presence_penalty_scale = ttk.Scale(config_frame, from_=0.0, to=1.0, variable=self.presence_penalty_var)
    #     self.presence_penalty_scale.set(0.0)  # Default value
    #     self.presence_penalty_label = ttk.Label(config_frame, textvariable=self.presence_penalty_var)
    #     self.presence_penalty_label.grid(row=7, column=1, padx=5, pady=5, sticky='n')
    #     self.presence_penalty_scale.grid(row=8, column=1, padx=5, pady=5, sticky='ew')

    #     # Button to apply changes
    #     apply_button = ttk.Button(config_frame, text='Apply', command=self.update_agent_settings)
    #     apply_button.grid(row=9, column=1, padx=5, pady=5, sticky='ew')

    # def update_agent_settings(self):
    #     self.model = self.model_entry.get() or "gpt-4-0613"
    #     self.temperature = float(self.temperature_var.get() or 0.3)
    #     self.top_p = float(self.top_p_var.get() or 1.0)
    #     self.frequency_penalty = float(self.frequency_penalty_var.get() or 0.0)
    #     self.presence_penalty = float(self.presence_penalty_var.get() or 0.0)

