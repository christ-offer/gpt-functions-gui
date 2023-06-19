
import openai
import json
import logging
from typing import Optional, Dict, List, Tuple

from functions import function_params, wikidata_sparql_query, scrape_webpage, write_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns, image_to_text, read_file, edit_file, list_history_entries, write_history_entry, read_history_entry, query_wolframalpha


system_message = """
PersonalAssistant:
===CONSTRAINTS===
You are genius level intelligent and knowledgable in every domain and field.
You think step by step to make sure you have the right solution
If you are unsure about the solution, or you are not sure you fully understood the problem, you ask for clarification
You only use your functions when they are called

===RESPONSE FORMAT===  
Review:
- Errorhandling suggestions;
- Performance suggestions;
- Bestpractices suggestions;
- Security suggestions;

Ticket:
- Title;
- Description;
- Requirements;
- Classes&functions;
- File structure;
- acceptance-criteria;

Brainstorm:
- Problem;
- Approach;
- Technology;
- Pros&Cons;

===COMMANDS===
/python [idea] - Calls the python_repl function.
/wolfram [question] - Calls the query_wolframalpha function
/wikidata [question] - Calls the wikidata_sparql_query function
/scrape [url] - Calls the scrape_webpage function
/write_code [idea] - Calls the write_file function
/kb_create [content] - Calls the knowledgebase_create_entry function
/kb_list - Calls the knowledgebase_list_entries function
/kb_read [entry_name] - Calls the knowledgebase_read_entry function
/list_history - Calls the list_history_entries function
/read_history [entry_name] - Calls the read_history_entry function
/write_history [content] - Summarizes the chat history, calls the write_history_entry function
/csv [filename] - Calls the read_csv_columns function
/read_file [filename] - Calls the read_file function
/edit_file [filename] [replacementcontent] - Calls the edit_file function
/image [image] - Calls the image_to_text function
/review - NOT A FUNCTION - Returns a review of the code following the response format
/ticket [solution] - NOT A FUNCTION - Returns a ticket for the solution following the response format
/brainstorm [n, topic] - NOT A FUNCTION - Returns a list of n ideas for the topic following the response format
/help - Returns a list of all available functions
"""

system_message2 = """
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
"""

def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({"role": "system", "content": system_message})
    conversation.append({"role": "user", "content": prompt})
    # Replace this with your actual OpenAI secret key
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=conversation,
        functions=function_params,
        function_call="auto",
    )

    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        print(f"Function name: {function_name}")
        print(f"Function arguments: {function_args}")

        if function_name == "python_repl":
            function_response = python_repl(function_args.get("code"))
        elif function_name == "query_wolframalpha":
            function_response = query_wolframalpha(function_args.get("query"))
        elif function_name == "knowledgebase_read_entry":
            function_response = knowledgebase_read_entry(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "read_history_entry":
            function_response = read_history_entry(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "write_history_entry":
            function_response = write_history_entry(*function_args.values())
        elif function_name == "list_history_entries":
            function_response = list_history_entries(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "knowledgebase_list_entries":
            function_response = knowledgebase_list_entries()
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation
        elif function_name in ["knowledgebase_create_entry","knowledgebase_update_entry", "read_csv_columns", "write_file"]:
            function_response = globals()[function_name](*function_args.values())
        elif function_name == "wikidata_sparql_query":
            function_response = wikidata_sparql_query(function_args.get("query"))
        elif function_name == "scrape_webpage":
            function_response = scrape_webpage(function_args.get("url"))
        elif function_name == "image_to_text":
            function_response = image_to_text(function_args.get("filename"))
        elif function_name == "read_file":
            function_response = read_file(function_args.get("filename"))
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "edit_file":
            filename = function_args.get("filepath")
            changes = function_args.get("changes")
            function_response = edit_file(filename, changes)

        logging.info(f"Function response: {function_response}")
        
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": system_message2},
                {"role": "user", "content": prompt},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        conversation.append(second_response["choices"][0]["message"]) 
        return second_response["choices"][0]["message"]["content"], conversation  # Return the conversation here
    else:
        conversation.append(message)
        return message["content"], conversation
