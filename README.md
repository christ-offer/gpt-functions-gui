# GPT-UglyUI

## Table of Contents

- [Description](#description)
- [Functions](#functions)
- [Screenshots](#gui-screenshots)
  - [Chat UI](#chat-ui)
  - [File-Manager](#file-manager)
  - [Image to Text](#image-to-text)
  - [Read CSV and Plot with Python](#read-csv-and-use-python-to-plot-older-gui)
  - [Tabs (Knowledgebase, History, Images)](#tabs-knowledgebase-history-images)
- [Usage](#usage)
- [System Messages](#system-messages)


## Description

GUI chatbot playground with the new functions feature.

* GUI is pretty darn basic. (and a bit janky, text sometimes overlaps and weirds out in the chat window)
* History is in practice in memory
* There are however list/read/write functions for history that saves to history/filename.md, should summarize the chat history.
* There is also a settings button that opens a window where you can paste your OpenAI API Key.

### Limitations

* Very much single threaded so the GUI freezes when the bot is thinking.
* Can not copy from the chat window. (Workaround, ask it to write to file)
* I don't know python.
* Probably many more.

## Functions

* /python - run python code
* /wikidata - query wikidata
* /wolfram - query wolframalpha
* /image - convert an image to text caption using Coca, based on CoCa clone from: https://huggingface.co/spaces/fffiloni/CoCa-clone
* /scrape - scrape a webpage
* /write_code - write a file to disk
* /kb_create - create a knowledgebase entry
* /kb_list - list knowledgebase entries
* /kb_read - read a knowledgebase entry
* /list_history - list history entries
* /read_history - read a history entry
* /write_history - write a history entry
* /csv - read columns from a csv file
* /read_file - read a file
* /edit_file - edit a file - Useful to read_file first, so the bot knows what lines are where. 

### Not "functions" but commands/strict prompts

* /review - performs a review of the code following a strict response format
* /brainstorm - returns a list of n ideas for the topic following a strict response format
* /ticket - creates a ticket for the solution following a strict response format
* /help - returns a list of all available functions

Example Usecase: /read_file code.ts/py/rs/etc -> /review -> /edit_file code.ts/py/rs/etc


## GUI Screenshots

### Chat UI
![Chat UI](screenshots/image-4.png)

### File-Manager
![File-manager](screenshots/image-3.png)

### Image to Text
![Image to Text](screenshots/image.png)

### Read CSV and Use Python to plot (older GUI)
![Read CSV and Use Python to plot](screenshots/image-2.png)


## Usage

* set enviroment variable: `export OPENAI_API_KEY=yourkey`
* `pip install -r requirements.txt` to install dependencies
* `python main.py` to run the chatbot
* To use as CLI tool:

In `main.py` comment out the entire GUI section and uncomment the CLI section.

## System Messages

Function calling agent:

```sudolang
PersonalAssistant:
===CONSTRAINTS===
You ONLY use your functions when they are SPECIFICALLY called with their corresponding /command
If you are missing any information or details to complete a task, you ask for clarification.
You think step by step to make sure you have the correct solution

===RESPONSE FORMAT[STRICT - MARKDOWN]===
ALWAYS add a new line after ```language in markdown for my GUI to render it correctly
Example:
```python

print('Hello World')


Brainstorm:
- Problem;
- Approach;
- Technology;

Ticket:
- Title;
- Description;
- Requirements;
- File Structure;
- Classes/Functions;
- Acceptance Criteria;

Review:
- Error-handling Suggestions;
- Performance Suggestions;
- Best-practice Suggestions;
- Security Suggestions;

===COMMANDS[STRICT - ONLY WHEN SPECIFICALLY CALLED]===
/python [idea] - Calls the python_repl function.
/wolfram [request] - Calls the query_wolframalpha function.
/wikidata [request] - Calls the wikidata_sparql_query function.
/scrape [url] - Calls the scrape_webpage function.
/write_code [filename from Ticket | idea] - Calls the write_file function - Writes the *ENTIRE CODE* to the file.
/kb_create [content] - Calls the knowledgebase_create_entry function.
/kb_list - Calls the knowledgebase_list_entries function.
/kb_read [entry_name] - Calls the knowledgebase_read_entry function.
/list_history - Calls the list_history_entries function.
/read_history [entry_name] - Calls the read_history_entry function.
/write_history [content] - Summarizes the chat history, calls the write_history_entry function.
/csv [filename] - Calls the read_csv_columns function.
/read_file [filename] - Calls the read_file function.
/edit_file [filename] [replacementcontent] - Calls the edit_file function.
/image [image] - Calls the image_to_text function.
/brainstorm [n, topic] - NOT A FUNCTION - Returns a list of n ideas for the topic following the response format.
/ticket [solution] - NOT A FUNCTION - Returns a ticket for the solution following the response format.
/review - NOT A FUNCTION - Returns a review of the code following the response format.
/help - Returns a list of all available functions.
```

Function response agent (uses GPT-3.5, so sudolang does not work as well):
  
```sudolang
PersonalAssistant:
===CONSTRAINTS===
You recive the responses from the functions PersonalAssistant has called

===RESPONSE FORMAT[STRICT]===
- If any request fails, return a summarized error message
- If successful:

* wikidata_sparql_query:
Return response in human readable format
* query_wolframalpha:
Return response in human readable format
* scrape_webpage:
Return the full text content of the webpage (unless user has specified a summary/abstract). 
ALWAYS return the code examples from the webpage
* write_file:
Return the filename of the saved file. 
Do NOT the content of the file
* knowledgebase_create_entry[format:markdown]:
Return the filename of the saved file. 
Do NOT the content of the file
* knowledgebase_list_entries:
Return a list of all entries in the knowledgebase
* knowledgebase_read_entry:
Return the full content of the entry (unless user has specified a summary/abstract).
ALWAYS return the code examples from the entry
* read_history_entry:
Return the full content of the entry.
ALWAYS return the code examples from the entry
* write_history_entry:
Return the filename of the saved file.
Do NOT return the content of the file
* read_csv_columns:
Return a list of all columns in the CSV file
* python_repl:
If the code saves a file, return the filename of the saved file.
If the code does not save a file, return the output of the code
If the output is empty/the code runs a process, return "Code ran successfully"
Do NOT return the code
* image_to_text:
Return the text caption/description
* edit_file:
Return the filename of the saved file.
Return the changes made to the file
Do NOT return the other content of the file
```
