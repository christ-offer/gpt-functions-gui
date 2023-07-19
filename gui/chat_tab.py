import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import N, S, E, W
import tiktoken
import markdown
from tkhtmlview import HTMLLabel

# CHAT TAB
def create_widgets_chat_window(self):
    self.chat_window.grid_rowconfigure(0, weight=1)  
    self.chat_window.grid_columnconfigure(0, weight=0)  
    self.chat_window.grid_columnconfigure(1, weight=0)  
    self.chat_window.grid_columnconfigure(2, weight=4)  
    ttk.Label(self.chat_window, text ="Chatbot").grid(column = 0, row = 0, padx = 30, pady = 30, sticky='nsew') 
    self.create_chat_sidebar(self.chat_window)
    self.create_chat_main(self.chat_window)

    # bind 'Enter' to run_chat function in Tab 1 only
    self.chat_window.bind('<Return>', self.ai_manager.run_chat)

def create_chat_sidebar(self, parent):
    self.sidebar = ttk.Frame(parent, width=200)
    self.sidebar.grid(row=0, column=0, sticky='ns')
    parent.grid_columnconfigure(0, minsize=200)  # column index of sidebar
    # Add a widget to make the sidebar visible. Adjust as necessary for your design.
    sidebar_label = ttk.Label(self.sidebar, text="Sidebar")
    sidebar_label.pack()
    
    
    # Add a reset button
    reset_button = ttk.Button(self.sidebar, text='Reset Conversation', command=self.reset_conversation, style='TButton')
    reset_button.pack()
    
    # Add an image upload button
    upload_button = ttk.Button(self.sidebar, text='Upload Image', command=self.file_manager.upload_image, style='TButton')
    upload_button.pack()
    
    # Add a csv upload button
    upload_csv_button = ttk.Button(self.sidebar, text='Upload CSV', command=self.file_manager.upload_csv, style='TButton')
    upload_csv_button.pack()
    
    # Add a display for total token count and cost
    self.total_token_count = tk.StringVar()
    self.total_token_count.set("Total tokens: 0")
    total_token_count_label = ttk.Label(self.sidebar, textvariable=self.total_token_count)
    total_token_count_label.pack()
    
    self.total_cost_of_input = tk.StringVar()
    self.total_cost_of_input.set("Total cost: 0$")
    total_cost_of_input_label = ttk.Label(self.sidebar, textvariable=self.total_cost_of_input)
    total_cost_of_input_label.pack()
    
    # Add a theme dropdown
    available_themes = self.root.get_themes()  # get the list of themes
    self.theme_var = tk.StringVar()  # create a StringVar to hold selected theme
    self.theme_var.set(self.root.set_theme)  # set initial value to the current theme
    theme_dropdown = ttk.Combobox(self.sidebar, textvariable=self.theme_var, values=available_themes)
    theme_dropdown.pack(side=tk.BOTTOM, anchor='s')
    theme_dropdown.bind('<<ComboboxSelected>>', self.styles.change_theme)  # bind the selection event to the change_theme method

def create_chat_main(self, parent):
    main_frame = ttk.Frame(parent)
    main_frame.grid(row=0, column=2, sticky=N+S+E+W)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    self.create_text_area(main_frame)
    self.create_input_area(main_frame)

def create_text_area(self, frame):
    self.text_area = HTMLLabel(frame, html="<p>Welcome to the chat!</p>", background="oldlace", font=('Ubuntu', 16))
    self.text_area.grid(row=0, column=0, sticky='nsew')
    self.current_html = "<p>Welcome to the chat!</p>"  # Initialize with the same content as the label

    
def update_token_count(self, event):
    # First, we reset the modified flag so the function doesn't run in a loop
    self.user_input_text.edit_modified(False)

    # Get the content of the text field
    content = self.user_input_text.get('1.0', 'end-1c')

    if content.strip() == "":
        # If the content is empty, manually set the token count and cost to 0
        token_count = 0
        input_cost = 0.0
    else:
        # Otherwise, calculate the token count and input cost
        token_count, input_cost = self.num_tokens_from_messages([{"content": content}])

    # Update the token_count StringVar
    self.token_count.set(f"Input token count: {token_count}")

    # Update the cost StringVar
    self.cost_of_input.set(f"Cost of input: {input_cost:.6f}$")
    
    
def num_tokens_from_messages(self, messages, model="gpt-4-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return self.num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    # Calculate cost of tokens
    if model is not None:
        if model == "gpt-3.5-turbo-0613":
            cost_per_token = 0.0000015
        elif model == "gpt-3.5-turbo-16k-0613":
            cost_per_token = 0.000003
        elif model == "gpt-4-0314":
            cost_per_token = 0.00003
        elif model == "gpt-4-32k-0314":
            cost_per_token = 0.00003
        elif model == "gpt-4-0613":
            cost_per_token = 0.00003
        elif model == "gpt-4-32k-0613":
            cost_per_token = 0.00003
        elif model == "gpt-4":
            cost_per_token = 0.00003
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}."""
            )
        cost = num_tokens * cost_per_token
    # Return an object with the number of tokens and the cost
    return num_tokens, cost

def create_input_area(self, frame):
    bottom_frame = ttk.Frame(frame)
    bottom_frame.grid(sticky='nsew')

    self.user_input_text = scrolledtext.ScrolledText(bottom_frame, wrap='word', background="oldlace", height=2, font=('Ubuntu', 16)) # Set the font size and height
    self.user_input_text.grid(row=0, column=0, sticky='nsew')
    
    # Bind the user_input_text widget to the Modified event
    self.user_input_text.bind('<<Modified>>', self.update_token_count)

    # Create a new frame for the counters
    counter_frame = ttk.Frame(bottom_frame)
    counter_frame.grid(row=2, column=0, sticky='nsew')

    # Move token and cost labels to counter_frame
    self.token_count = tk.StringVar()
    self.cost_of_input = tk.StringVar()
    self.token_count.set("Input token count: 0")
    self.cost_of_input.set("Cost of input: 0$")
    token_label = tk.Label(counter_frame, textvariable=self.token_count)
    cost_label = tk.Label(counter_frame, textvariable=self.cost_of_input)
    token_label.pack(side='top')
    cost_label.pack(side='top')

    send_button = ttk.Button(bottom_frame, text='Send', command=self.ai_manager.run_chat, style='TButton')
    send_button.grid(row=1, column=0)

    bottom_frame.grid_columnconfigure(0, weight=1)
    
def update_text_area(self, response):
    # Stop the loading animation
    html = markdown.markdown(response)
    self.is_loading = False
    self.loading_label.grid_remove()  # Remove the loading label from the application window
    # Create HTML for the response
    response_html = f'<p style="background-color: lightblue;">Bot: {html}</p><br/>'

    # Append the new message to the existing HTML content and update the widget
    self.current_html += response_html
    self.text_area.set_html(self.current_html)


def reset_conversation(self):
    self.conversation = []
    self.total_cost = 0
    self.total_tokens = 0
    reset_html = "<p>Conversation reset.</p>"
    self.text_area.set_html(reset_html)
    self.current_html = reset_html
    chatbot_gui.total_token_count.set(f"Total tokens: 0")
    chatbot_gui.total_cost_of_input.set(f"Total cost: 0$")