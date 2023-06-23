
import openai
from openai.error import OpenAIError
import json
import logging
from typing import Optional, Dict, List, Tuple
import re

from agents.csv_agent import CSVHandler
from agents.python_agent import PythonRepl
from agents.kb_agent import KnowledgebaseHandler
from agents.history_agent import HistoryHandler
from agents.file_write_agent import FileWriter
from agents.scrape_agent import Scraper
from agents.wikidata_agent import WikidataAgent
from agents.image_agent import ImageAgent
from agents.help_agent import HelpAgent
from agents.function_call_agent import FunctionCallAgent

from system_messages.system import function_response_agent, review_agent, brainstorm_agent, ticket_agent, base_system_message

csv_handler = CSVHandler()
python_repl = PythonRepl()
kb_handler = KnowledgebaseHandler()
history_handler = HistoryHandler()
file_handler = FileWriter()
scraper = Scraper()
wikidata_agent = WikidataAgent()
image_agent = ImageAgent()
help_agent = HelpAgent()
functions = FunctionCallAgent()


def get_command(prompt):
    """Extract command from prompt if it exists"""
    match = re.search(r"/\w+", prompt)
    if match:
        return match.group(0)
    return None

def call_function(function_name, function_args):
    if function_name not in functions.function_map:
        raise Exception(f"Function {function_name} not found.")
    if function_args is None:
        return functions.function_map[function_name]()
    return functions.function_map[function_name](*function_args.values())


def function_call_agent(
        prompt, 
        conversation, 
        system_message,
        function_params,
        model: str = "gpt-4-0613", 
        temperature: float = 0.3, 
        top_p: float = 1.0, 
        frequency_penalty: float = 0.0, 
        presence_penalty: float = 0.0):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=[
                {"role": "system", "content": system_message}
            ] + conversation + [
                {"role": "user", "content": prompt}
            ],
            functions=function_params,
            function_call="auto",
        )
    except OpenAIError as error:
        logging.error(f"OpenAI API call failed: {str(error)}")
        return "OpenAI API call failed due to an internal server error.", conversation
    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return "Failed to connect to OpenAI.", conversation
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return "Requests exceed OpenAI rate limit.", conversation
    return response["choices"][0]["message"], conversation


def regular_agent(
        prompt,
        conversation,
        system_message,
        model: str = "gpt-4-0613",
        temperature: float = 0.6,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=[
                {"role": "system", "content": system_message},
            ] + conversation + [
                {"role": "user", "content": prompt}
            ],
        )
    except OpenAIError as error:
        logging.error(f"OpenAI API call failed: {str(error)}")
        return "OpenAI API call failed due to an internal server error.", conversation
    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return "Failed to connect to OpenAI.", conversation
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return "Requests exceed OpenAI rate limit.", conversation
    return response["choices"][0]["message"], conversation

def afunction_response_agent(
        prompt,
        conversation,
        system_message,
        model = "gpt-3.5-turbo-16k-0613",
        temperature = 0.0,
        top_p = 1.0,
        frequency_penalty = 0.0,
        presence_penalty = 0.0,
        function_response: any = None,
        function_name: str = None,
        message: str = None
        ):
    try:
        print(function_response)
        response = openai.ChatCompletion.create(
            model=model,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=[
                    {"role": "system", "content": function_response_agent},
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
        logging.error(f"OpenAI API call failed: {str(error)}")
        return "OpenAI API call failed due to an internal server error." + function_response, conversation
    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return "Failed to connect to OpenAI." + function_response, conversation
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return "Requests exceed OpenAI rate limit." + function_response, conversation
    conversation.append({
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }) 
    return response["choices"][0]["message"], conversation

def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({
        "role": "user",
        "content": prompt,
    })
    if get_command(prompt) == "/csv":
        print("CSV Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=csv_handler.system_message, 
            function_params=csv_handler.read_csv_columns_params,
            temperature=csv_handler.temperature,
            top_p=csv_handler.top_p,
            frequency_penalty=csv_handler.frequency_penalty,
            model=csv_handler.model,
            )
        message = response[0]
    elif get_command(prompt) == "/python":
        print("Python Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=python_repl.system_message, 
            function_params=python_repl.python_repl_params,
            temperature=python_repl.temperature,
            top_p=python_repl.top_p,
            frequency_penalty=python_repl.frequency_penalty,
            model=python_repl.model,
            )
        message = response[0]
    elif get_command(prompt) == "/kb":
        print("Knowledge Base Agent")
        prompt = prompt[3:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=kb_handler.system_message, 
            function_params=kb_handler.knowledgebase_params,
            temperature=kb_handler.temperature,
            top_p=kb_handler.top_p,
            frequency_penalty=kb_handler.frequency_penalty,
            model=kb_handler.model,
            )
        message = response[0]
    elif get_command(prompt) == "/history":
        print("History Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=history_handler.system_message, 
            function_params=history_handler.history_params,
            temperature=history_handler.temperature,
            top_p=history_handler.top_p,
            frequency_penalty=history_handler.frequency_penalty,
            model=history_handler.model,
            )
        message = response[0]
    elif get_command(prompt) == "/write":
        print("Write Code Agent")
        prompt = prompt[6:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=file_handler.write_system_message, 
            function_params=file_handler.write_file_params,
            temperature=file_handler.temperature,
            top_p=file_handler.top_p,
            frequency_penalty=file_handler.frequency_penalty,
            model=file_handler.model,
            )
        message = response[0]
    elif get_command(prompt) == "/read":
        print("Read File Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=file_handler.read_system_message, 
            function_params=file_handler.read_file_params,
            temperature=file_handler.temperature,
            top_p=file_handler.top_p,
            frequency_penalty=file_handler.frequency_penalty,
            model=file_handler.model,
            )
        message = response[0]
    elif get_command(prompt) == "/edit":
        print("Edit File Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=file_handler.edit_system_message, 
            function_params=file_handler.edit_file_params,
            temperature=file_handler.temperature,
            top_p=file_handler.top_p,
            frequency_penalty=file_handler.frequency_penalty,
            model=file_handler.model,
            )
        message = response[0]
    elif get_command(prompt) == "/wikidata":
        print("Wikidata Agent")
        prompt = prompt[9:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=wikidata_agent.system_message, 
            function_params=wikidata_agent.wikidata_sparql_query_params,
            temperature=wikidata_agent.temperature,
            top_p=wikidata_agent.top_p,
            frequency_penalty=wikidata_agent.frequency_penalty,
            model=wikidata_agent.model,
            )
        message = response[0]
    elif get_command(prompt) == "/scrape":
        print("Scrape Webpage Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=scraper.system_message, 
            function_params=scraper.scrape_webpage_params,
            temperature=scraper.temperature,
            top_p=scraper.top_p,
            frequency_penalty=scraper.frequency_penalty,
            model=scraper.model,
            )
        message = response[0]
    elif get_command(prompt) == "/image":
        print("Image to Text Agent")
        prompt = prompt[7:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=image_agent.system_message, 
            function_params=image_agent.image_to_text_params,
            temperature=image_agent.temperature,
            top_p=image_agent.top_p,
            frequency_penalty=image_agent.frequency_penalty,
            model=image_agent.model,
            )
        message = response[0]
    elif get_command(prompt) == "/help":
        print("Help Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=help_agent.system_message, 
            function_params=help_agent.help_params,
            temperature=help_agent.temperature,
            top_p=help_agent.top_p,
            frequency_penalty=help_agent.frequency_penalty,
            model=help_agent.model,
            )
        message = response[0]
    elif get_command(prompt) == "/review":
        print("Review Agent")
        prompt = prompt[7:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=review_agent
            )
        message = response[0]
    elif get_command(prompt) == "/brainstorm":
        print("Brainstorm Agent")
        prompt = prompt[10:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=brainstorm_agent
            )
        message = response[0]
    elif get_command(prompt) == "/ticket":
        print("Ticket Agent")
        prompt = prompt[7:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=ticket_agent
            )
        message = response[0]
    else:
        print('Personal Assistant')
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=base_system_message
            )
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
            #response = afunction_response_agent(prompt=prompt, conversation=conversation, system_message=function_response_agent, function_name=function_name, function_response=function_response)
            #return response[0], response[1]
            try:
                second_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k-0613",
                    temperature=0.0,
                    messages=[
                        {"role": "system", "content": function_response_agent},
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
                logging.error(f"OpenAI API call failed: {str(error)}")
                return "OpenAI API call failed due to an internal server error." + function_response, conversation
            except openai.error.APIConnectionError as e:
                print(f"Failed to connect to OpenAI API: {e}")
                return "Failed to connect to OpenAI." + function_response, conversation
            except openai.error.RateLimitError as e:
                print(f"OpenAI API request exceeded rate limit: {e}")
                return "Requests exceed OpenAI rate limit." + function_response, conversation
            
            conversation.append({
                "role": "assistant",
                "content": second_response["choices"][0]["message"]["content"],
            }) 
            return second_response["choices"][0]["message"]["content"], conversation
    else:
        conversation.append({
            "role": "assistant",
            "content": message["content"],
        })
        return message["content"], conversation
