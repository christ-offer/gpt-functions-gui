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
