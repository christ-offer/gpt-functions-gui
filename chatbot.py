
import openai
from openai.error import OpenAIError
import json
import logging
from typing import Optional, Dict, List, Tuple

from system import system_message, system_message2
from functions import (
    function_params, 
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
    query_wolframalpha, 
    knowledgebase_update_entry
)

FUNCTIONS_THAT_APPEND_TO_CONVERSATION = {
    "knowledgebase_read_entry", 
    "read_history_entry", 
    "list_history_entries", 
    "knowledgebase_list_entries", 
    "read_file"
}

FUNCTION_MAP = {
    "python_repl": python_repl,
    "query_wolframalpha": query_wolframalpha,
    "knowledgebase_read_entry": knowledgebase_read_entry,
    "read_history_entry": read_history_entry,
    "write_history_entry": write_history_entry,
    "list_history_entries": list_history_entries,
    "knowledgebase_list_entries": knowledgebase_list_entries,
    "knowledgebase_create_entry": knowledgebase_create_entry,
    "knowledgebase_update_entry": knowledgebase_update_entry,
    "read_csv_columns": read_csv_columns,
    "write_file": write_file,
    "wikidata_sparql_query": wikidata_sparql_query,
    "scrape_webpage": scrape_webpage,
    "image_to_text": image_to_text,
    "read_file": read_file,
    "edit_file": edit_file
}

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
    conversation.append({"role": "system", "content": system_message})
    conversation.append({"role": "user", "content": prompt})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=conversation,
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
                return "OpenAI API call failed due to an internal server error.", conversation
            except openai.error.APIConnectionError as e:
                #Handle connection error here
                print(f"Failed to connect to OpenAI API: {e}")
                return "Failed to connect to OpenAI.", conversation
                
            except openai.error.RateLimitError as e:
                #Handle rate limit error (we recommend using exponential backoff)
                print(f"OpenAI API request exceeded rate limit: {e}")
                return "Requests exceed OpenAI rate limit.", conversation
            conversation.append(second_response["choices"][0]["message"]) 
            return second_response["choices"][0]["message"]["content"], conversation  # Return the conversation here
    else:
        conversation.append(message)
        return message["content"], conversation
