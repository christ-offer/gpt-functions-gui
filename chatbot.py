
import openai
from openai.error import OpenAIError
import json
import logging
from typing import Optional, Dict, List, Tuple
import re

from system import system_message2
from functions import (
    # Function parameters
    knowledgebase_params,
    history_params,
    python_repl_params,
    write_file_params,
    read_csv_columns_params,
    wikidata_sparql_query_params,
    scrape_webpage_params,
    image_to_text_params,
    read_file_params,
    edit_file_params,
    help_params,
    # Function implementations
    wikidata_sparql_query, 
    scrape_webpage, 
    write_file, 
    knowledgebase_create_entry, 
    knowledgebase_list_entries, 
    knowledgebase_read_entry, 
    python_repl, 
    read_csv_columns, 
    image_to_text, 
    read_file, 
    edit_file, 
    list_history_entries, 
    write_history_entry, 
    read_history_entry, 
    help,
    # System messages
    edit_file_system_message,
    read_file_system_message,
    write_file_system_message,
    scrape_system_message,
    wikidata_system_message,
    image_to_text_system_message,
    csv_system_message,
    knowledgebase_system_message,
    python_repl_system_message,
    history_system_message,
    help_system_message,
)

FUNCTIONS_THAT_APPEND_TO_CONVERSATION = {
    "knowledgebase_read_entry", 
    "knowledgebase_list_entries", 
    "read_history_entry", 
    "list_history_entries", 
    "read_file",
    "read_csv_columns",
    "scrape_webpage",
}

FUNCTION_MAP = {
    "python_repl": python_repl,
    "knowledgebase_read_entry": knowledgebase_read_entry,
    "read_history_entry": read_history_entry,
    "write_history_entry": write_history_entry,
    "list_history_entries": list_history_entries,
    "knowledgebase_list_entries": knowledgebase_list_entries,
    "knowledgebase_create_entry": knowledgebase_create_entry,
    "read_csv_columns": read_csv_columns,
    "write_file": write_file,
    "wikidata_sparql_query": wikidata_sparql_query,
    "scrape_webpage": scrape_webpage,
    "image_to_text": image_to_text,
    "read_file": read_file,
    "edit_file": edit_file,
    "help": help,
}

def get_command(prompt):
    """Extract command from prompt if it exists"""
    match = re.search(r"/\w+", prompt)
    if match:
        return match.group(0)
    return None

def call_function(function_name, function_args):
    # Check if the function exists
    if function_name not in FUNCTION_MAP:
        raise Exception(f"Function {function_name} not found.")
    
    # Check if the function_args is None, if it is, call the function without arguments
    if function_args is None:
        return FUNCTION_MAP[function_name]()
    
    # If the function_args is not None, call the function with the arguments
    return FUNCTION_MAP[function_name](*function_args.values())


def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({
        "role": "user",
        "content": prompt,
    })
    if get_command(prompt) == "/csv":
        print("CSV Agent")
        prompt = prompt[5:].strip()
        function_params = read_csv_columns_params
        system_message = csv_system_message
    elif get_command(prompt) == "/python":
        print("Python Agent")
        prompt = prompt[8:].strip()
        function_params = python_repl_params
        system_message = python_repl_system_message
    elif get_command(prompt) == "/kb":
        print("Knowledge Base Agent")
        prompt = prompt[3:].strip()
        function_params = knowledgebase_params
        system_message = knowledgebase_system_message
    elif get_command(prompt) == "/history":
        print("History Agent")
        prompt = prompt[8:].strip()
        function_params = history_params
        system_message = history_system_message
    elif get_command(prompt) == "/write":
        print("Write Code Agent")
        prompt = prompt[6:].strip()
        function_params = write_file_params
        system_message = write_file_system_message
    elif get_command(prompt) == "/read":
        print("Read File Agent")
        prompt = prompt[5:].strip()
        function_params = read_file_params
        system_message = read_file_system_message
    elif get_command(prompt) == "/edit":
        print("Edit File Agent")
        prompt = prompt[5:].strip()
        function_params = edit_file_params
        system_message = edit_file_system_message
    elif get_command(prompt) == "/wikidata":
        print("Wikidata Agent")
        prompt = prompt[9:].strip()
        function_params = wikidata_sparql_query_params
        system_message = wikidata_system_message
    elif get_command(prompt) == "/scrape":
        print("Scrape Webpage Agent")
        prompt = prompt[8:].strip()
        function_params = scrape_webpage_params
        system_message = scrape_system_message
    elif get_command(prompt) == "/image":
        print("Image to Text Agent")
        prompt = prompt[7:].strip()
        function_params = image_to_text_params
        system_message = image_to_text_system_message
    else:
        function_params = help_params
        system_message = help_system_message
    
    print(f"Function name: {function_params['function_name']}")
    print(f"Function parameters: {function_params}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": system_message}
            ] + conversation + [
                {"role": "user", "content": prompt}
            ],
            functions=function_params,
            function_call="auto",
        )
    except OpenAIError as error:
        # Log the detailed error for debugging, but only return a generic message to the user
        logging.error(f"OpenAI API call failed: {str(error)}")
        return "OpenAI API call failed due to an internal server error.", conversation
    except openai.error.APIConnectionError as e:
        #Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")
        return "Failed to connect to OpenAI.", conversation
        
    except openai.error.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI API request exceeded rate limit: {e}")
        return "Requests exceed OpenAI rate limit.", conversation
    
    message = response["choices"][0]["message"]
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        print(f"Function name: {function_name}")
        print(f"Function arguments: {function_args}")
        
        function_response = call_function(function_name, function_args)
        
        if function_name in FUNCTIONS_THAT_APPEND_TO_CONVERSATION:
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        else:
            logging.info(f"Function response: {function_response}")
            
            try:
                second_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k-0613",
                    messages=[
                        {"role": "system", "content": system_message2},
                        {"role": "user", "content": prompt},
                        #{"role": "assistant", "content": message},
                        message,
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        },
                    ],
                )
            except OpenAIError as error:
                # Log the detailed error for debugging, but only return a generic message to the user
                logging.error(f"OpenAI API call failed: {str(error)}")
                return "OpenAI API call failed due to an internal server error." + function_response, conversation
            except openai.error.APIConnectionError as e:
                #Handle connection error here
                print(f"Failed to connect to OpenAI API: {e}")
                return "Failed to connect to OpenAI." + function_response, conversation
                
            except openai.error.RateLimitError as e:
                #Handle rate limit error (we recommend using exponential backoff)
                print(f"OpenAI API request exceeded rate limit: {e}")
                return "Requests exceed OpenAI rate limit." + function_response, conversation
            
            conversation.append({
                "role": "assistant",
                "content": second_response["choices"][0]["message"]["content"],
            }) 
            return second_response["choices"][0]["message"]["content"], conversation  # Return the conversation here
    else:
        conversation.append({
            "role": "assistant",
            "content": message["content"],
        })
        return message["content"], conversation
