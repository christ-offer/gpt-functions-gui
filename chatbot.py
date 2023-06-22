
import openai
from openai.error import OpenAIError
import json
import logging
from typing import Optional, Dict, List, Tuple
import re

from system import function_response_agent, review_agent, brainstorm_agent, ticket_agent, base_system_message
import functions as func

# Using classes
class FunctionCallAgent:
    def __init__(self):
        self.functions_that_append_to_conversation = {
            "knowledgebase_read_entry", 
            "knowledgebase_list_entries", 
            "read_history_entry", 
            "list_history_entries", 
            "read_file",
            "read_csv_columns",
            "scrape_webpage",
        }

        self.function_map = {
            "python_repl": func.python_repl,
            "knowledgebase_read_entry": func.knowledgebase_read_entry,
            "read_history_entry": func.read_history_entry,
            "write_history_entry": func.write_history_entry,
            "list_history_entries": func.list_history_entries,
            "knowledgebase_list_entries": func.knowledgebase_list_entries,
            "knowledgebase_create_entry": func.knowledgebase_create_entry,
            "read_csv_columns": func.read_csv_columns,
            "write_file": func.write_file,
            "wikidata_sparql_query": func.wikidata_sparql_query,
            "scrape_webpage": func.scrape_webpage,
            "image_to_text": func.image_to_text,
            "read_file": func.read_file,
            "edit_file": func.edit_file,
            "help": func.help,
        }

functions = FunctionCallAgent()
MODEL = "gpt-4-0613"
TEMPERATURE = 0.3
TOP_P = 1.0
FREQUENCY_PENALTY = 0.0
PRESENCE_PENALTY = 0.0

def get_command(prompt):
    """Extract command from prompt if it exists"""
    match = re.search(r"/\w+", prompt)
    if match:
        return match.group(0)
    return None

def call_function(function_name, function_args):
    # Check if the function exists
    if function_name not in functions.function_map:
        raise Exception(f"Function {function_name} not found.")
    
    # Check if the function_args is None, if it is, call the function without arguments
    if function_args is None:
        return functions.function_map[function_name]()
    
    # If the function_args is not None, call the function with the arguments
    return functions.function_map[function_name](*function_args.values())


def function_call_agent(
        prompt, 
        conversation, 
        system_message,
        function_params,
        model = MODEL, 
        temperature = TEMPERATURE, 
        top_p = TOP_P, 
        frequency_penalty = FREQUENCY_PENALTY, 
        presence_penalty = PRESENCE_PENALTY):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            temperature=0.3,
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
    return response["choices"][0]["message"], conversation


def regular_agent(
        prompt,
        conversation,
        system_message,
        model = MODEL,
        temperature = TEMPERATURE,
        top_p = TOP_P,
        frequency_penalty = FREQUENCY_PENALTY,
        presence_penalty = PRESENCE_PENALTY):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            temperature=0.65,
            messages=[
                {"role": "system", "content": system_message},
            ] + conversation + [
                {"role": "user", "content": prompt}
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
    return response["choices"][0]["message"], conversation


def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({
        "role": "user",
        "content": prompt,
    })
    if get_command(prompt) == "/csv":
        print("CSV Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.csv_system_message, function_params=func.read_csv_columns_params)
        message = response[0]
    elif get_command(prompt) == "/python":
        print("Python Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.python_repl_system_message, function_params=func.python_repl_params)
        message = response[0]
    elif get_command(prompt) == "/kb":
        print("Knowledge Base Agent")
        prompt = prompt[3:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.knowledgebase_system_message, function_params=func.knowledgebase_params)
        message = response[0]
    elif get_command(prompt) == "/history":
        print("History Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.history_system_message, function_params=func.history_params)
        message = response[0]
    elif get_command(prompt) == "/write":
        print("Write Code Agent")
        prompt = prompt[6:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.write_file_system_message, function_params=func.write_file_params)
        message = response[0]
    elif get_command(prompt) == "/read":
        print("Read File Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.read_file_system_message, function_params=func.read_file_params)
        message = response[0]
    elif get_command(prompt) == "/edit":
        print("Edit File Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.edit_file_system_message, function_params=func.edit_file_params)
        message = response[0]
    elif get_command(prompt) == "/wikidata":
        print("Wikidata Agent")
        prompt = prompt[9:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.wikidata_system_message, function_params=func.wikidata_sparql_query_params)
        message = response[0]
    elif get_command(prompt) == "/scrape":
        print("Scrape Webpage Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.scrape_system_message, function_params=func.scrape_webpage_params)
        message = response[0]
    elif get_command(prompt) == "/image":
        print("Image to Text Agent")
        prompt = prompt[7:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.image_to_text_system_message, function_params=func.image_to_text_params)
        message = response[0]
    elif get_command(prompt) == "/review":
        print("Review Agent")
        prompt = prompt[7:].strip()
        response = regular_agent(prompt=prompt, conversation=conversation, system_message=review_agent)
        message = response[0]
    elif get_command(prompt) == "/brainstorm":
        print("Brainstorm Agent")
        prompt = prompt[10:].strip()
        response = regular_agent(prompt=prompt, conversation=conversation, system_message=brainstorm_agent)
        message = response[0]
    elif get_command(prompt) == "/ticket":
        print("Ticket Agent")
        prompt = prompt[7:].strip()
        response = regular_agent(prompt=prompt, conversation=conversation, system_message=ticket_agent)
        message = response[0]
    elif get_command(prompt) == "/help":
        print("Help Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(prompt=prompt, conversation=conversation, system_message=func.help_system_message, function_params=func.help_params)
        message = response[0]
    else:
        print('Personal Assistant')
        response = regular_agent(prompt=prompt, conversation=conversation, system_message=base_system_message)
        message = response[0]    

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        print(f"Function name: {function_name}")
        print(f"Function arguments: {function_args}")
        
        function_response = call_function(function_name, function_args)
        
        if function_name in functions.functions_that_append_to_conversation:
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
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": function_response_agent},
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
